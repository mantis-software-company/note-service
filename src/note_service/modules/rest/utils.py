class ResponseObject:
    def __init__(self, data={}, message=None, status=None, exceptionDetail=None, page={}):
        self.data = data
        self.message = message
        self.statusCode = self._render_status_code(status) if status else None
        self.exceptionDetail = exceptionDetail
        self.page = page
    
    def _render_status_code(self, s):
        if s == 200:
            return "OK-200"
        elif s == 201:
            return "CREATED-201"
        elif s >= 400:
            return f"EX-{s}"


class PaginationObject:
    def __init__(self, page, total, total_pages):
        self.page = page
        self.total = total
        self.total_pages = total_pages