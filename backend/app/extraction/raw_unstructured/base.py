class BaseExtractor:
    def extract(self, file_path: str) -> str:
        raise NotImplementedError
