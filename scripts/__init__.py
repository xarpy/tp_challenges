try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
except ModuleNotFoundError:
    pass

__all__ = ["search_engine", "company_details", "count_employees"]
