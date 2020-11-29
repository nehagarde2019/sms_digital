def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('login', '/login')
    config.add_route('get_all_chemicals', 'get-all-chemicals')
    config.add_route('get_commodity_by_id', 'get-commodity-by-id/{id}')
    config.add_route('update_commodity_by_id', 'update-commodity-by-id')
    config.add_route('remove_composition_by_id', 'remove-composition-by-id')
    config.add_route('add_composition_by_id', 'add-composition-by-id')
