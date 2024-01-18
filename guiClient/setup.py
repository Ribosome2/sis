from cx_Freeze import setup, Executable

setup(
    name="SearchClient",
    version="1.0",
    description="Search Client Application",
    executables=[Executable("search-client.py")]
)