import warnings

# Suppress Pydantic NotRequired warnings
warnings.filterwarnings('ignore', message='typing.NotRequired is not a Python type')
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')

print("Warning filters applied successfully")
