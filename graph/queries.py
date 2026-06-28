# graph/queries.py

def get_entity_network(driver, account_id, hops=2):
    with driver.session() as s:
        result = s.run("""
            MATCH path = (a:Account {account_id: $account_id})-[*1..$hops]-(other)
            RETURN path
        """, account_id=account_id, hops=hops)
        return [record["path"] for record in result]

def find_circular_flows(driver):
    with driver.session() as s:
        result = s.run("""
            MATCH (a1:Account)-[:TRANSFERS_TO]->(a2:Account)
                              -[:TRANSFERS_TO]->(a3:Account)
                              -[:TRANSFERS_TO]->(a1)
            RETURN a1.account_id, a2.account_id, a3.account_id
        """)
        return result.data()

def get_customer_full_profile(driver, customer_id):
    with driver.session() as s:
        result = s.run("""
            MATCH (c:Customer {customer_id: $customer_id})
            OPTIONAL MATCH (c)-[:OWNS]->(co:Company)
            OPTIONAL MATCH (c)-[:LINKED_TO]->(a:Account)
            OPTIONAL MATCH (a)-[:HAS_ALERT]->(al:Alert)
            RETURN c, collect(distinct co) as companies,
                   collect(distinct a) as accounts,
                   collect(distinct al) as alerts
        """, customer_id=customer_id)
        return result.single()