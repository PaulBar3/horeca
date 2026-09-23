from django import template

register = template.Library()


@register.inclusion_tag("partials/_pagination.html", takes_context=True)
def paginate(context, page_obj, window=2):
    """Windowed pagination (current ±2, always first/last) keeping query params."""
    if not page_obj or not page_obj.has_other_pages():
        return {"pages": []}

    current = page_obj.number
    total = page_obj.paginator.num_pages
    numbers = {n for n in range(current - window, current + window + 1) if 1 <= n <= total}
    numbers.update({1, total})

    request = context.get("request")

    def url_for(number):
        if request:
            query = request.GET.copy()
            query["page"] = str(number)
            return f"?{query.urlencode()}"
        return f"?page={number}"

    pages = []
    previous = None
    for number in sorted(numbers):
        if previous is not None and number - previous > 1:
            pages.append({"n": None, "url": "", "is_current": False})
        pages.append({
            "n": number,
            "url": url_for(number),
            "is_current": number == current,
        })
        previous = number

    return {
        "pages": pages,
        "prev_url": url_for(current - 1) if page_obj.has_previous() else "",
        "next_url": url_for(current + 1) if page_obj.has_next() else "",
    }
