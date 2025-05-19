-- Function to execute SQL statements
CREATE OR REPLACE FUNCTION execute_sql(sql_statement text)
RETURNS void AS $$
BEGIN
    EXECUTE sql_statement;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 