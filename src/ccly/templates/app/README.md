# __APP_NAME__

A Django app packaged for PyPI. Load it with ccly:

```bash
pip install -e .
ccly init __APP_NAME__
ccly migrate
ccly runserver
```

`GET /__APP_NAME__/health/` returns the JSON string `"OK"`.

Put deployment-wide values, such as an external API URL, in `ccly_settings.py`. Uppercase names there are added to the ccly Django settings.
