pipeline {
    agent any
    
    environment {
        // AWS Configuration
        AWS_REGION = 'af-south-1'
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        ECR_REPOSITORY = 'mycandidate'
        ECS_CLUSTER = 'mycandidate-cluster'
        ECS_SERVICE = 'mycandidate-service'
        ECS_TASK_DEFINITION = 'mycandidate-task'
        
        // Docker Configuration
        DOCKER_IMAGE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"
        DOCKER_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
        
        // Python Configuration
        PYTHON_VERSION = '3.10.9'
        
        // Test Configuration
        PYTHONPATH = "${WORKSPACE}"
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Lint and Code Quality') {
            parallel {
                stage('Flake8 Linting') {
                    steps {
                        script {
                            docker.image("python:${PYTHON_VERSION}-slim").inside {
                                sh '''
                                    pip install --quiet flake8
                                    flake8 --version
                                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                                    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                                '''
                            }
                        }
                    }
                }
                
                stage('Pylint Analysis') {
                    steps {
                        script {
                            docker.image("python:${PYTHON_VERSION}-slim").inside {
                                sh '''
                                    pip install --quiet pylint
                                    pylint --version
                                    pylint main/ --exit-zero || true
                                '''
                            }
                        }
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    docker.image("python:${PYTHON_VERSION}-slim").inside {
                    sh '''
                        pip install --quiet -r requirements.txt
                        pip install --quiet pytest pytest-cov
                        export PYTHONPATH=${WORKSPACE}
                        pytest tests/ -v --cov=main --cov-report=xml --cov-report=html --cov-report=term
                    '''
                    }
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: '**/test-results.xml'
                    publishCoverage adapters: [
                        coberturaAdapter('**/coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Security Scanning') {
            parallel {
                stage('Dependency Scanning') {
                    steps {
                        script {
                            // Using OWASP Dependency-Check- OSS
                            sh '''
                                if [ ! -f dependency-check/bin/dependency-check.sh ]; then
                                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.9/dependency-check-9.0.9-release.zip
                                    unzip -q dependency-check-9.0.9-release.zip
                                    mv dependency-check dependency-check
                                fi
                                dependency-check/bin/dependency-check.sh \
                                    --project "MyCandidate" \
                                    --scan . \
                                    --format JSON \
                                    --format HTML \
                                    --out reports/ \
                                    --enableExperimental \
                                    --failOnCVSS 7 || true
                            '''
                        }
                    }
                    post {
                        always {
                            publishHTML([
                                reportName: 'Dependency Check Report',
                                reportDir: 'reports',
                                reportFiles: 'dependency-check-report.html',
                                keepAll: true
                            ])
                        }
                    }
                }
                
                stage('Secrets Scanning') {
                    steps {
                        script {
                            sh '''
                                # Using TruffleHog for secrets scanning
                                docker run --rm -v "$PWD:/pwd" trufflesecurity/trufflehog:latest \
                                    filesystem /pwd --json > reports/trufflehog-report.json || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Authenticate to ECR
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${DOCKER_IMAGE}
                    '''
                    
                    // Build Docker image
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        
        stage('Container Image Scanning') {
            steps {
                script {
                    // Using Trivy for container scanning
                    sh '''
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                            -v $PWD/reports:/reports \
                            aquasec/trivy:latest image \
                            --format json --output /reports/trivy-report.json \
                            ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                        
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                            -v $PWD/reports:/reports \
                            aquasec/trivy:latest image \
                            --format html --output /reports/trivy-report.html \
                            ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    '''
                }
            }
            post {
                always {
                    publishHTML([
                        reportName: 'Trivy Security Scan',
                        reportDir: 'reports',
                        reportFiles: 'trivy-report.html',
                        keepAll: true
                    ])
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    sh '''
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        
        stage('Update ECS Task Definition') {
            steps {
                script {
                    // Get current task definition
                    sh '''
                        aws ecs describe-task-definition \
                            --task-definition ${ECS_TASK_DEFINITION} \
                            --region ${AWS_REGION} \
                            --query taskDefinition > task-definition.json
                    '''
                    
                    // Update image in task definition
                    sh '''
                        # Use jq to update the image in task definition
                        cat task-definition.json | \
                        jq ".containerDefinitions[0].image = \\"${DOCKER_IMAGE}:${DOCKER_TAG}\\"" > task-definition-updated.json
                    '''
                    
                    // Register new task definition
                    sh '''
                        aws ecs register-task-definition \
                            --cli-input-json file://task-definition-updated.json \
                            --region ${AWS_REGION} > task-definition-registered.json
                    '''
                    
                    // Get new task definition revision
                    script {
                        env.NEW_TASK_DEF_REV = sh(
                            script: 'cat task-definition-registered.json | jq -r ".taskDefinition.revision"',
                            returnStdout: true
                        ).trim()
                    }
                }
            }
        }
        
        stage('Deploy to ECS') {
            steps {
                script {
                    // Update ECS service with new task definition
                    sh '''
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER} \
                            --service ${ECS_SERVICE} \
                            --task-definition ${ECS_TASK_DEFINITION}:${NEW_TASK_DEF_REV} \
                            --region ${AWS_REGION} \
                            --force-new-deployment
                    '''
                    
                    // Wait for service to stabilize
                    sh '''
                        aws ecs wait services-stable \
                            --cluster ${ECS_CLUSTER} \
                            --services ${ECS_SERVICE} \
                            --region ${AWS_REGION}
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    // Get ALB endpoint from AWS
                    script {
                        env.ALB_ENDPOINT = sh(
                            script: '''
                                aws elbv2 describe-load-balancers \
                                    --region ${AWS_REGION} \
                                    --query "LoadBalancers[?contains(LoadBalancerName, 'mycandidate')].DNSName" \
                                    --output text
                            ''',
                            returnStdout: true
                        ).trim()
                    }
                    
                    // Run smoke tests
                    sh '''
                        # Wait for service to be ready
                        sleep 30
                        
                        # Test health endpoint
                        curl -f https://${ALB_ENDPOINT}/api/v1/health || exit 1
                        
                        # Test API endpoint (if test data exists)
                        curl -f https://${ALB_ENDPOINT}/api/v1/wards/TEST_WARD/candidates || true
                    '''
                }
            }
        }
    }
    
    post {
        success {
            script {
                echo "Deployment successful! Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                // Send notification (Slack, email, etc.)
            }
        }
        
        failure {
            script {
                echo "Deployment failed! Attempting rollback..."
                
                // Rollback to previous task definition
                sh '''
                    # Get previous task definition revision
                    PREV_REV=$((NEW_TASK_DEF_REV - 1))
                    
                    if [ $PREV_REV -gt 0 ]; then
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER} \
                            --service ${ECS_SERVICE} \
                            --task-definition ${ECS_TASK_DEFINITION}:${PREV_REV} \
                            --region ${AWS_REGION} \
                            --force-new-deployment
                        
                        echo "Rolled back to task definition revision ${PREV_REV}"
                    else
                        echo "No previous revision to rollback to"
                    fi
                '''
                
                // Send failure notification
            }
        }
        
        always {
            // Cleanup
            sh '''
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                docker rmi ${DOCKER_IMAGE}:latest || true
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }
    }
}

