# Start Django development server
# Uses 'py' launcher (works even when 'python' alias is blocked by Windows Store)
Set-Location "$PSScriptRoot\backend"
py manage.py runserver --settings=config.settings.development
