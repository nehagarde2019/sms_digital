import asyncio
from datetime import datetime

from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from .. import models

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@view_config(route_name='login', renderer='json')
def login_view(request):
    try:
        query = request.dbsession.query(models.User)
        user = query.filter(models.User.email == 'neha.r.garde@gmail.com',
                            models.User.password == 'Pass@123').first()

        if user:
            return {'result': 'ok', 'token': request.create_jwt_token(user.id)}
        else:
            return {'result': 'error', 'token': None}
    except DBAPIError:
        return Response("Error", content_type='text/plain', status=500)
    return {'one': 'one', 'user_email': user.email, 'user_password': user.password}


async def get_chemicals(request):
    try:
        await asyncio.sleep(1)
        chemicals = request.dbsession.query(models.Chemical).all()

        all_data = [{
            'id': chemical.id,
            'name': chemical.name,
        } for chemical in chemicals]
        return all_data
    except DBAPIError:
        return Response("Error", content_type='text/plain', status=500)


@view_config(route_name='get_all_chemicals', renderer='json')
def get_all_chemicals_view(request):
    if request.authenticated_userid:
        all_data = loop.run_until_complete(get_chemicals(request))
        return {'List of chemicals: ': all_data}
    else:
        return {'message': "Unauthenticated user"}


async def get_commodity(request, comm_id):
    try:
        await asyncio.sleep(1)
        commodity_id = comm_id
        sql = """
                SELECT comm.id,comm.name,comm.inventory,comm.price,
                JSON_AGG(
                    JSON_BUILD_OBJECT('id', c.id, 'name', c.name,'percentage',e.comm->'percentage')
                )
                FROM commodity comm
                INNER JOIN LATERAL JSONB_ARRAY_ELEMENTS(comm.chemical_composition) AS e(comm) ON TRUE
                INNER JOIN chemical c ON (e.comm->'id')::text::int = c.id
                WHERE comm.id=""" + commodity_id + """
                group by comm.id
            """
        commodity = request.dbsession.execute(sql)

        data_details = {}
        for data in commodity:
            for column, value in data.items():
                data_details[column] = value
        return data_details
    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)


@view_config(route_name='get_commodity_by_id', renderer='json', request_method='GET')
def get_commodity_by_id_view(request):
    if request.authenticated_userid:
        data_details = loop.run_until_complete(get_commodity(request, request.matchdict['id']))
        return {'Commodity Details: ': data_details}
    else:
        return {'message': "Unauthenticated user", 'time': datetime.datetime.now()}


async def update_commodity(request):
    try:
        commodity_info = request.json_body
        del commodity_info['id']
        request.dbsession.query(models.Commodity).filter(models.Commodity.id == commodity_info['id']) \
            .update(commodity_info)
    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)
    return True


@view_config(route_name='update_commodity_by_id', renderer='json', request_method='PUT')
def update_commodity_by_id_view(request):
    if request.authenticated_userid:
        if update_commodity(request):
            return {"message": "Commodity updated Successfully"}
    else:
        return {'message': "Unauthenticated user"}


async def remove_composition(request):
    try:
        commodity_info = request.json_body
        commodity_id = commodity_info['commodity_id']
        element_id = commodity_info['element_id']

        chemical_composition = request.dbsession.query(models.Commodity). \
            filter(models.Commodity.id == commodity_id).one_or_none().chemical_composition

        new_comp = []
        total_percentage = 0
        for chem_id, chemical in enumerate(chemical_composition):
            if not (chemical['id'] == element_id or chemical['id'] == 0):
                total_percentage += chemical['percentage']
                new_comp.append(chemical)
        new_comp.append({'id': 0, 'percentage': 100 - total_percentage})

        request.dbsession.query(models.Commodity).filter(models.Commodity.id == commodity_id) \
            .update({'chemical_composition': new_comp})

    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)
    return True


@view_config(route_name='remove_composition_by_id', renderer='json', request_method='PUT')
def remove_composition_by_id_view(request):
    if request.authenticated_userid:
        if remove_composition(request):
            return {'message': 'Composition removed Successfully'}
    else:
        return {'message': 'Unauthenticated user'}


async def add_composition(request):
    try:
        commodity_info = request.json_body
        commodity_id = commodity_info['commodity_id']
        element_id = commodity_info['element_id']
        percentage = commodity_info['percentage']
        chemical_composition = request.dbsession.query(models.Commodity). \
            filter(models.Commodity.id == commodity_id).one_or_none().chemical_composition

        new_comp = []
        total_percentage = 0
        flag = False
        for chem_id, chemical in enumerate(chemical_composition):
            if not (chemical['id'] == 0 or element_id == chemical['id']):
                total_percentage += chemical['percentage']
                new_comp.append(chemical)
            if element_id == chemical['id'] and (total_percentage + percentage <= 100):
                total_percentage += percentage
                new_comp.append({'id': element_id, 'percentage': percentage})
                flag = True
            elif element_id == chemical['id'] and (total_percentage + percentage > 100):
                return {'message': 'Cannot update. Total percentage exceeds 100. '}

        if not flag and (total_percentage + percentage <= 100):
            new_comp.append({'id': element_id, 'percentage': percentage})
            total_percentage += percentage
        if not flag and (total_percentage + percentage > 100):
            return {'message': 'Cannot update. Total percentage exceeds 100. '}

        new_comp.append({'id': 0, 'percentage': 100 - total_percentage})
        request.dbsession.query(models.Commodity).filter(models.Commodity.id == commodity_id) \
            .update({'chemical_composition': new_comp})

    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)


@view_config(route_name='add_composition_by_id', renderer='json', request_method='PUT')
def add_composition_by_id_view(request):
    if request.authenticated_userid:
        if add_composition(request):
            return {'message': 'Data updated successfully'}
    else:
        return {'message': 'Unauthenticated user'}
