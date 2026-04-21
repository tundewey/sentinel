"""Lambda adapter for Sentinel API."""

from mangum import Mangum

from main import app


handler = Mangum(app)
