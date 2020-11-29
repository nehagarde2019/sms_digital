import asyncio
from datetime import datetime

import colander
from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sms_digi.schemas.api_schema import RemoveCommodityCompositionElementSchema, UpdateCommoditySchema, \
    AddCommodityCompositionElementSchema
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
    return {'user_email': user.email, 'user_password': user.password}


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


async def get_commodity(request):
    try:
        await asyncio.sleep(1)

        sql = """
                SELECT comm.id,comm.name,comm.inventory,comm.price,
                JSON_AGG(
                    JSON_BUILD_OBJECT('id', c.id, 'name', c.name,'percentage',e.comm->'percentage')
                )
                FROM commodity comm
                INNER JOIN LATERAL JSONB_ARRAY_ELEMENTS(comm.chemical_composition) AS e(comm) ON TRUE
                INNER JOIN chemical c ON (e.comm->'id')::text::int = c.id
                WHERE comm.id=""" + request.matchdict['id'] + """
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
        data_details = loop.run_until_complete(get_commodity(request))
        return {'Commodity Details: ': data_details}
    else:
        return {'message': "Unauthenticated user"}


async def update_commodity(request):
    try:
        await asyncio.sleep(1)
        get_comm_object = request.dbsession.query(models.Commodity).\
            filter(models.Commodity.id == request.json_body['id'])
        commodity_exists = get_comm_object.all()
        if commodity_exists:
            commodity_info = request.json_body
            del commodity_info['id']
            get_comm_object.update(commodity_info)
        else:
            return False
    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)
    return True


@view_config(route_name='update_commodity_by_id', renderer='json', request_method='PUT')
def update_commodity_by_id_view(request):
    if request.authenticated_userid:
        try:
            UpdateCommoditySchema().deserialize(request.json_body)
            if loop.run_until_complete(update_commodity(request)):
                return {"message": "Commodity updated Successfully"}
            else:
                return {"message": "Commodity does not exist."}
        except colander.Invalid as e:
            return {'message': 'Invalid Input Parameters', 'details': str(e)}
    else:
        return {'message': "Unauthenticated user"}


async def remove_composition(request):
    try:
        await asyncio.sleep(1)
        commodity_info = request.json_body
        commodity_id = commodity_info['commodity_id']
        element_id = commodity_info['element_id']

        chemical_composition = request.dbsession.query(models.Commodity). \
            filter(models.Commodity.id == commodity_id).all()

        if chemical_composition:
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
        else:
            return False

    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)
    return True


@view_config(route_name='remove_composition_by_id', renderer='json', request_method='PUT')
def remove_composition_by_id_view(request):
    if request.authenticated_userid:
        try:
            RemoveCommodityCompositionElementSchema().deserialize(request.json_body)
            if loop.run_until_complete(remove_composition(request)):
                return {'message': 'Composition removed Successfully.'}
            else:
                return {'message': 'Composition could not be removed.'}
        except colander.Invalid as e:
            return {'message': 'Invalid Input Parameters','details':str(e)}
    else:
        return {'message': 'Unauthenticated user'}


async def add_composition(request):
    try:
        await asyncio.sleep(1)
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
                return False

        if not flag and (total_percentage + percentage <= 100):
            new_comp.append({'id': element_id, 'percentage': percentage})
            total_percentage += percentage
        if not flag and (total_percentage + percentage > 100):
            return False

        new_comp.append({'id': 0, 'percentage': 100 - total_percentage})
        request.dbsession.query(models.Commodity).filter(models.Commodity.id == commodity_id) \
            .update({'chemical_composition': new_comp})
        return True
    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)


@view_config(route_name='add_composition_by_id', renderer='json', request_method='PUT')
def add_composition_by_id_view(request):
    if request.authenticated_userid:
        try:
            AddCommodityCompositionElementSchema().deserialize(request.json_body)
            if loop.run_until_complete(add_composition(request)):
                return {'message': 'Composition element added successfully'}
            else:
                return {'message': 'Percentage exceeds 100'}
        except colander.Invalid as e:
            return {'message': 'Invalid Input Parameters', 'details': str(e)}
    else:
        return {'message': 'Unauthenticated user'}
