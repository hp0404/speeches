# -*- coding: utf-8 -*-
from sqlmodel import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URI)