from unittest.mock import MagicMock

from pymetastore.htypes import (
    HCharType,
    HDecimalType,
    HListType,
    HMapType,
    HPrimitiveType,
    HStructType,
    HUnionType,
    HVarcharType,
    PrimitiveCategory,
)
from pymetastore.metastore import HMS, HColumn

from recap.readers.hive_metastore import HiveMetastoreReader
from recap.types import (
    BoolType,
    BytesType,
    FloatType,
    IntType,
    ListType,
    MapType,
    NullType,
    StringType,
    StructType,
    UnionType,
)


def test_struct():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn("col1", HPrimitiveType(PrimitiveCategory.BOOLEAN)),
            HColumn("col2", HPrimitiveType(PrimitiveCategory.BYTE)),
            HColumn("col3", HPrimitiveType(PrimitiveCategory.SHORT)),
            HColumn("col4", HPrimitiveType(PrimitiveCategory.INT)),
            HColumn("col5", HPrimitiveType(PrimitiveCategory.LONG)),
            HColumn("col6", HPrimitiveType(PrimitiveCategory.FLOAT)),
            HColumn("col7", HPrimitiveType(PrimitiveCategory.DOUBLE)),
            HColumn("col8", HPrimitiveType(PrimitiveCategory.STRING)),
            HColumn("col9", HPrimitiveType(PrimitiveCategory.BINARY)),
            HColumn("col10", HDecimalType(10, 2)),
            HColumn("col11", HVarcharType(100)),
            HColumn("col12", HCharType(100)),
            HColumn("col13", HPrimitiveType(PrimitiveCategory.VOID)),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    # Check that the schema was converted correctly.
    assert isinstance(result, StructType)
    assert len(result.fields) == 13

    # Validate each column in the order defined in MockTable
    assert isinstance(result.fields[0], UnionType)
    assert isinstance(result.fields[0].types[1], BoolType)
    assert result.fields[0].extra_attrs["name"] == "col1"

    assert isinstance(result.fields[1], UnionType)
    assert isinstance(result.fields[1].types[1], IntType)
    assert result.fields[1].types[1].bits == 8
    assert result.fields[1].extra_attrs["name"] == "col2"

    assert isinstance(result.fields[2], UnionType)
    assert isinstance(result.fields[2].types[1], IntType)
    assert result.fields[2].types[1].bits == 16
    assert result.fields[2].extra_attrs["name"] == "col3"

    assert isinstance(result.fields[3], UnionType)
    assert isinstance(result.fields[3].types[1], IntType)
    assert result.fields[3].types[1].bits == 32
    assert result.fields[3].extra_attrs["name"] == "col4"

    assert isinstance(result.fields[4], UnionType)
    assert isinstance(result.fields[4].types[1], IntType)
    assert result.fields[4].types[1].bits == 64
    assert result.fields[4].extra_attrs["name"] == "col5"

    assert isinstance(result.fields[5], UnionType)
    assert isinstance(result.fields[5].types[1], FloatType)
    assert result.fields[5].types[1].bits == 32
    assert result.fields[5].extra_attrs["name"] == "col6"

    assert isinstance(result.fields[6], UnionType)
    assert isinstance(result.fields[6].types[1], FloatType)
    assert result.fields[6].types[1].bits == 64
    assert result.fields[6].extra_attrs["name"] == "col7"

    assert isinstance(result.fields[7], UnionType)
    assert isinstance(result.fields[7].types[1], StringType)
    assert result.fields[7].types[1].bytes_ == 9_223_372_036_854_775_807
    assert result.fields[7].extra_attrs["name"] == "col8"

    assert isinstance(result.fields[8], UnionType)
    assert isinstance(result.fields[8].types[1], BytesType)
    assert result.fields[8].types[1].bytes_ == 2_147_483_647
    assert result.fields[8].extra_attrs["name"] == "col9"

    assert isinstance(result.fields[9], UnionType)
    assert isinstance(result.fields[9].types[1], BytesType)
    assert result.fields[9].types[1].bytes_ == 16
    assert result.fields[9].types[1].extra_attrs["precision"] == 10
    assert result.fields[9].types[1].extra_attrs["scale"] == 2
    assert result.fields[9].extra_attrs["name"] == "col10"

    assert isinstance(result.fields[10], UnionType)
    assert isinstance(result.fields[10].types[1], StringType)
    assert result.fields[10].types[1].bytes_ == 100
    assert result.fields[10].extra_attrs["name"] == "col11"

    assert isinstance(result.fields[11], UnionType)
    assert isinstance(result.fields[11].types[1], StringType)
    assert result.fields[11].types[1].bytes_ == 100
    assert not result.fields[11].types[1].variable
    assert result.fields[11].extra_attrs["name"] == "col12"

    assert isinstance(result.fields[12], NullType)
    assert result.fields[12].extra_attrs["name"] == "col13"


def test_struct_with_struct_type():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn(
                "col1",
                HStructType(
                    names=["sub_col1", "sub_col2"],
                    types=[
                        HPrimitiveType(PrimitiveCategory.BOOLEAN),
                        HPrimitiveType(PrimitiveCategory.INT),
                    ],
                ),
            ),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    # Check that the schema was converted correctly.
    assert isinstance(result, StructType)
    assert len(result.fields) == 1

    # Validate the column with StructType
    assert isinstance(result.fields[0], UnionType)
    assert isinstance(result.fields[0].types[1], StructType)
    assert result.fields[0].extra_attrs["name"] == "col1"

    # Validate sub-columns of the struct
    struct_field = result.fields[0].types[1]
    assert len(struct_field.fields) == 2

    # Validate sub_col1
    assert isinstance(struct_field.fields[0], UnionType)
    assert isinstance(struct_field.fields[0].types[1], BoolType)
    assert struct_field.fields[0].extra_attrs["name"] == "sub_col1"

    # Validate sub_col2
    assert isinstance(struct_field.fields[1], UnionType)
    assert isinstance(struct_field.fields[1].types[1], IntType)
    assert struct_field.fields[1].types[1].bits == 32
    assert struct_field.fields[1].extra_attrs["name"] == "sub_col2"


def test_struct_with_list_type():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn("col1", HListType(HPrimitiveType(PrimitiveCategory.BOOLEAN))),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    assert isinstance(result, StructType)
    assert len(result.fields) == 1
    assert isinstance(result.fields[0], UnionType)
    assert isinstance(result.fields[0].types[1], ListType)
    assert isinstance(result.fields[0].types[1].values, UnionType)
    assert isinstance(result.fields[0].types[1].values.types[1], BoolType)
    assert result.fields[0].extra_attrs["name"] == "col1"


def test_struct_with_map_type():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn(
                "col1",
                HMapType(
                    HPrimitiveType(PrimitiveCategory.STRING),
                    HPrimitiveType(PrimitiveCategory.INT),
                ),
            ),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    assert isinstance(result, StructType)
    assert len(result.fields) == 1
    assert isinstance(result.fields[0], UnionType)
    assert isinstance(result.fields[0].types[1], MapType)
    assert isinstance(result.fields[0].types[1].keys, UnionType)
    assert isinstance(result.fields[0].types[1].values, UnionType)
    assert isinstance(result.fields[0].types[1].keys.types[1], StringType)
    assert isinstance(result.fields[0].types[1].values.types[1], IntType)
    assert result.fields[0].extra_attrs["name"] == "col1"


def test_struct_with_nested_struct_type():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn(
                "col1",
                HStructType(
                    names=["sub_col1", "sub_col2"],
                    types=[
                        HStructType(
                            names=["nested_col1", "nested_col2"],
                            types=[
                                HPrimitiveType(PrimitiveCategory.BOOLEAN),
                                HPrimitiveType(PrimitiveCategory.INT),
                            ],
                        ),
                        HPrimitiveType(PrimitiveCategory.STRING),
                    ],
                ),
            ),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    # Check that the schema was converted correctly.
    assert isinstance(result, StructType)
    assert len(result.fields) == 1

    # Validate the column with StructType
    assert isinstance(result.fields[0], UnionType)
    assert isinstance(result.fields[0].types[1], StructType)
    assert result.fields[0].extra_attrs["name"] == "col1"

    # Validate sub-columns of the struct
    struct_field = result.fields[0].types[1]
    assert len(struct_field.fields) == 2

    # Validate sub_col1, which is another struct
    assert isinstance(struct_field.fields[0], UnionType)
    assert isinstance(struct_field.fields[0].types[1], StructType)
    assert struct_field.fields[0].extra_attrs["name"] == "sub_col1"

    # Validate nested_col1 and nested_col2 within sub_col1
    nested_struct_field = struct_field.fields[0].types[1]
    assert len(nested_struct_field.fields) == 2

    assert isinstance(nested_struct_field.fields[0], UnionType)
    assert isinstance(nested_struct_field.fields[0].types[1], BoolType)
    assert nested_struct_field.fields[0].extra_attrs["name"] == "nested_col1"

    assert isinstance(nested_struct_field.fields[1], UnionType)
    assert isinstance(nested_struct_field.fields[1].types[1], IntType)
    assert nested_struct_field.fields[1].types[1].bits == 32
    assert nested_struct_field.fields[1].extra_attrs["name"] == "nested_col2"

    # Validate sub_col2
    assert isinstance(struct_field.fields[1], UnionType)
    assert isinstance(struct_field.fields[1].types[1], StringType)
    assert struct_field.fields[1].types[1].bytes_ == 9_223_372_036_854_775_807
    assert struct_field.fields[1].extra_attrs["name"] == "sub_col2"


def test_struct_with_union_type():
    mock_client = MagicMock(spec=HMS)

    class MockTable:
        name = "dummy_table"
        columns = [
            HColumn(
                "col1",
                HUnionType(
                    [
                        HPrimitiveType(PrimitiveCategory.BOOLEAN),
                        HPrimitiveType(PrimitiveCategory.INT),
                    ]
                ),
            ),
        ]

    mock_client.get_table.return_value = MockTable

    reader = HiveMetastoreReader(mock_client)
    result = reader.struct("dummy_database", "dummy_table")

    assert isinstance(result, StructType)
    assert len(result.fields) == 1
    assert isinstance(result.fields[0], UnionType)
    assert result.fields[0].extra_attrs["name"] == "col1"
    assert len(result.fields[0].types) == 3  # null type + two types from HUnionType
    assert isinstance(result.fields[0].types[0], NullType)
    assert isinstance(result.fields[0].types[1], BoolType)
    assert isinstance(result.fields[0].types[2], IntType)
