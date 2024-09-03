from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict

class SEO(BaseModel):
    seo: List[str] = Field(description="SEO keywords used in the blog")
class URLS(BaseModel):
    urls: List[str] = Field(description="All hyperlinks/urls in the blog")
class Outlines(BaseModel):
    outline: Dict[str, List[str]] = Field(description="Headings as keys and subheadings as values") 