class BaseDashboardWidget:
    # The number of columns the widget should span. The dashboard grid spans 4 columns.
    col_span = 1

    # The rendered output can be parsed as JSX to allow more powerful
    # integration into the Django Headless admin.
    use_jsx = False

    def render(self, request) -> str:
        """
        The HTML that should be rendered inside the widget.
        """
        return ""

    def to_json(self, request) -> dict:
        return {
            "col_span": self.col_span,
            "use_jsx": self.use_jsx,
            "html": self.render(request),
        }


class RecentActivityWidget(BaseDashboardWidget):
    """
    A widget for showing the recent activity of the current user,
    similar to the one in the classic Django admin.
    """

    col_span = 2

    use_jsx = True

    def render(self, request):
        return "<RecentActionsWidget />"
