from ...app import db
from sqlalchemy import Column, Integer, String
from wtforms import SelectField, validators
from ...forms import Form
from main.database.base_class import Base

class Config(Base):
    """
    For site settings
    """
    __tablename__ = 'site_settings'

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String)
    title_short = Column(String)
    favicon_logo = Column(String)
    logo_colour = Column(String)
    footer_colour = Column(String)
    nav_bars_colour = Column(String)
    body_foreground_colour = Column(String)
    body_background_colour = Column(String)
    find_candidates_button = Column(String)
    candidate_names_colour = Column(String)
    data_schemas = Column(String)
    partner_name = Column(String)
    partner_website = Column(String)
    google_analytics_key = Column(String)
    gtag_script = Column(String)
    organization_name = Column(String)
    organization_link = Column(String)
    regional_explainer = Column(String)
    provincial_explainer = Column(String)
    national_explainer = Column(String)

    def __repr__(self):
        return f'<id {self.id}>'
    
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'short_title': self.title_short,
            'favicon_logo': self.favicon_logo,
            'logo_colour': self.logo_colour,
            'footer_colour': self.footer_colour,
            'nav_bars_colour': self.nav_bars_colour,
            'body_foreground_colour': self.body_foreground_colour,
            'body_background_colour': self.body_background_colour,
            'find_candidates_button': self.find_candidates_button,
            'candidate_names_colour': self.candidate_names_colour,
            'partner_name': self.partner_name,
            'partner_website': self.partner_website,
            'google_analytics_key': self.google_analytics_key,
            'gtag_script': self.gtag_script,
            'organization_name': self.organization_name,
            'organization_link': self.organization_link,
            'regional_explainer': self.regional_explainer,
            'provincial_explainer': self.provincial_explainer,
            'national_explainer': self.national_explainer
        }