# def test_cmd_list_tables_default_schema(runner):
#     result = runner.invoke(main.app, ["tables"])
#     expected_output = {"SCHEMA": "public", "TABLE": TEST_TABLE, "ROWS": "0"}
#     assert result.exit_code == 0
#     for col_header, col_value in expected_output.items():
#         assert col_header in result.stdout
#         assert col_value in result.stdout
#
#
# def test_cmd_list_tables_unknown_schema(runner):
#     result = runner.invoke(main.app, ["tables", "--schema", "monkeys_in_space"])
#     assert result.exit_code == 1
#     assert "Error: schema not found" in result.stdout
