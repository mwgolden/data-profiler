report_queries = {
    "obj_path_query" : """select path as Path, count(1) as Occurrences 
                            from df where json_type = 'object'
                            group by path, object_depth
                            order by object_depth, Path;""",
    "key_coverage_query": """select 
                            source_key, 
                            count(*) cnt,
                            round(100.0 * count(*) / t.tot, 2) as pct_coverage
                        from df
                        cross join (
                            select count(*) as tot
                            from df 
                            where path = '{0}' and json_type = 'object'
                        ) t
                        where parent_path = '{0}' and source_key is not null
                        group by source_key, t.tot 
                        order by cnt desc;""",
    "root_object_type": """select c.json_type
                            from df p
                            join df c on c.parent_path = p.path
                            where p.json_type = 'root';""",
    "object_instances": """select count(*) as object_instance_count
                            from df 
                            where json_type='object';""",
    "distinct_object_paths": """select count(distinct path) as distinct_path_count
                                from df 
                                where json_type='object';""",
    "distinct_keys": """select count(distinct source_key) as distinct_key_count
                        from df
                        where json_type != 'root';""",
    "path_distribution": """select json_type, count(distinct path) as distinct_paths
                            from df 
                            where json_type != 'root'
                            group by json_type;""",
    "array_path_count": """select count(distinct path) as array_path_count
                            from df
                            where instance_path != path and parent_path = path;""",
    "array_paths": """select 
                        path, json_depth,
                        count(distinct instance_path) as element_count
                        from df
                        where instance_path != path and parent_path = path
                        group by path,json_depth
                        order by json_depth;""",
    "max_depth": """select max(json_depth) as max_depth from df;"""
}