import colander


class UpdateCommoditySchema(colander.MappingSchema):
    id = colander.SchemaNode(colander.Integer())
    name = colander.SchemaNode(colander.String(), missing=colander.drop)
    inventory = colander.SchemaNode(colander.Float(), missing=colander.drop)
    price = colander.SchemaNode(colander.Float(), missing=colander.drop)


class RemoveCommodityCompositionElementSchema(colander.MappingSchema):
    commodity_id = colander.SchemaNode(colander.Integer())
    element_id = colander.SchemaNode(colander.Integer(), validator=colander.NoneOf([0]))


class AddCommodityCompositionElementSchema(colander.MappingSchema):
    commodity_id = colander.SchemaNode(colander.Integer())
    element_id = colander.SchemaNode(colander.Integer(), validator=colander.NoneOf([0]))
    percentage = colander.SchemaNode(colander.Float(), validator=colander.Range(0, 100))

