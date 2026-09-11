report_queries = {
    "obj_path_query" : """select path, json_type, object_depth, count(1) as occurrences 
                            from df where json_type = 'object'
                            group by path, json_type, object_depth
                            order by object_depth, path;""",
    "key_coverage_query": """select 
                            source_key, 
                            count(*) cnt,
                            t.tot,
                            round(100.0 * count(*) / t.tot, 2) as pct_coverage
                        from df
                        cross join (
                            select count(*) as tot
                            from df 
                            where path = '{0}' and json_type = 'object'
                        ) t
                        where parent_path = '{0}' and source_key is not null
                        group by source_key, t.tot 
                        order by cnt desc;"""
}