# What's in this PR?

This PR introduces a comprehensive REST API module, enhanced testing infrastructure, and improved documentation for the MyCandidate application. The changes focus on API separation, container runtime flexibility (Docker/Podman), and comprehensive testing capabilities.

## 🎯 Key Features

### 1. **New REST API Module** (`main/api.py`)
- Created dedicated API blueprint with `/api/v1` prefix for clean API separation
- **Health Check Endpoint**: `/api/v1/health` - Returns application and database status
- **Wards Candidates Endpoint**: `/api/v1/wards/<ward_id>/candidates` - Retrieves candidates by ward with optional `candidate_type` filtering
  - Supports filtering by candidate types: `national`, `provincial`, `local`, `national_regional`
  - Dynamically searches across different candidate type locators
  - Returns structured JSON with ward_id, candidates array, and count

### 2. **Comprehensive API Testing Suite** (`test-api.sh`)
- **557-line comprehensive test script** covering all aspects of the application
- **Container Runtime Selection**: Interactive prompt for Docker/Podman (defaults to Podman)
- **Automated Testing**:
  - Database connectivity and table validation
  - Redis connectivity checks
  - API endpoint testing with real data from database
  - Container health status validation
  - Database seeding verification
  - Error handling and edge case testing
- **Smart Data Retrieval**: Dynamically fetches actual `list_type` values from database for realistic testing
- **Color-coded Test Results**: Clear pass/fail indicators with detailed summaries
- **12+ comprehensive tests** covering all API endpoints and system components

### 3. **Documentation Enhancements** (`README.md`)
- **Docker/Podman Quick Start Guide**: Step-by-step instructions for containerized setup
- **API Documentation References**: Links to detailed API documentation
- **AWS Deployment Section**: References to architecture documentation
- **CI/CD Pipeline Information**: Details about Jenkins pipeline integration
- **Environment Variable Documentation**: Clear configuration guidance

### 4. **Code Organization**
- **API Blueprint Registration**: Clean separation of API routes in `main/core.py`
- **Minor Fixes**: Trailing newline corrections in `main/routes.py`

## 📋 Changes Made

### New Files
- `main/api.py` - REST API endpoints module
- `test-api.sh` - Comprehensive API testing script (557 lines)

### Modified Files
- `main/core.py` - Registered API blueprint
- `main/routes.py` - Minor formatting fix
- `README.md` - Added Docker/Podman guide, API docs, AWS deployment info

### Infrastructure (from commit history)
- `.dockerignore` - Docker build optimizations
- `docker-compose.yml` - Container orchestration updates
- `AWS_ARCHITECTURE.md` - Architecture documentation
- `Jenkinsfile` - CI/CD pipeline configuration
- Configuration updates for Redis and PostgreSQL URLs

## 🧪 Testing

Run the comprehensive test suite:

```bash
./test-api.sh
```

**Test Coverage:**
- ✅ Database connectivity and seeding
- ✅ Redis connectivity
- ✅ Health check endpoint (`/api/v1/health`)
- ✅ Wards candidates endpoint with various filters
- ✅ Error handling (404, 405, invalid endpoints)
- ✅ API response structure validation
- ✅ Candidate data structure validation
- ✅ Container health status
- ✅ Database table existence checks

**Expected Results:**
- Total Tests: 12+
- All tests should pass with proper setup

## 🚀 API Usage Examples

**Health Check:**
```bash
curl http://localhost:5001/api/v1/health
```

**Get Candidates by Ward:**
```bash
curl http://localhost:5001/api/v1/wards/Provincial/candidates
```

**Get Candidates with Type Filter:**
```bash
curl http://localhost:5001/api/v1/wards/Provincial/candidates?candidate_type=provincial
```

## 🔧 Technical Details

- **API Version**: v1 (`/api/v1`)
- **Container Runtime Support**: Docker and Podman (defaults to Podman)
- **Database**: PostgreSQL with dynamic query building based on candidate locators
- **Caching**: Redis integration ready
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes

## 📝 Commit History Summary

- `5290081` - add test script that defaults to podman
- `826e138` - update readme, use podman for local testing
- `6f53a84` - register api for separation
- `e966ad7` - revert redundant endpoint, keep health in new api
- `5c04933` - add health api
- `13feb88` - mount tests to container
- `7ddde1f` - update redis and postgres url
- `834356b` - add docker ignore
- `6633e63` - architecture design
- `00cc521` - update and add mermaid flow chart for architecture design

## ✅ Benefits

1. **Clean API Separation**: API routes are now isolated in their own blueprint
2. **Comprehensive Testing**: Automated test suite ensures API reliability
3. **Container Flexibility**: Support for both Docker and Podman runtimes
4. **Better Documentation**: Clear setup and usage instructions
5. **Production Ready**: Health checks and error handling suitable for production deployment
