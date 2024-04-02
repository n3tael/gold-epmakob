def check_sorting(sorting):
    if sorting not in ('total_votes', 'created_at', 'uploaded_at'):
        return 'uploaded_at'

    return sorting

def check_order(order):
    if order not in ('ASC', 'DESC'):
        return 'ASC'

    return order