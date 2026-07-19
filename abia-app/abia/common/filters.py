def apply_query_filters(qs, request, filter_map, search_field=None):
    p = request.query_params
    for param, field in filter_map.items():
        if v := p.get(param):
            qs = qs.filter(**{field: v})
    if search_field and (s := p.get("search")):
        qs = qs.filter(**{f"{search_field}__icontains": s})
    if o := p.get("ordering"):
        qs = qs.order_by(o)
    return qs
