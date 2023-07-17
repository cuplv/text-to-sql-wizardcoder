import json,argparse
from datasets import load_dataset
from natsql2sql.preprocess.sq import SubQuestion
from natsql2sql.natsql_parser import create_sql_from_natSQL
from natsql2sql.natsql2sql import Args


def construct_hyper_param():
    parser = argparse.ArgumentParser()
    parser.add_argument('--table_file', default='./data/tables_for_natsql.json', type=str)
    parser.add_argument("--natsql_file", default="actual_queries.json", type=str, help="output table.json")
    parser.add_argument('--output_file', default="predict_natsql2sql.txt", type=str, help="output file")
    parser.add_argument('--input_file', default="predict_natsql.txt", type=str, help="input file")
    parser.add_argument('--remove_groupby_from_natsql', action='store_true', default=True)
    parser.add_argument('--test_executable_natsql', action='store_true', default=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    
    # 1. Hyper parameters
    args = construct_hyper_param()
    
    # Preprocessing step added from second script
    dataset = load_dataset("richardr1126/spider-natsql-context-validation")
    queries = []
    with open(args.input_file, 'r') as input_file:
        for idx, line in enumerate(input_file):
            components = line.split('|')
            actual_query = components[1].strip()
            db_id = dataset["validation"][idx]["db_id"]
            queries.append({"NatSQL": actual_query, "db_id": db_id})
    with open(args.natsql_file, 'w') as output_file:
        json.dump(queries, output_file, indent=4)
    
    natsql2sql_args = Args()
    if args.remove_groupby_from_natsql:
        natsql2sql_args.not_infer_group = False
    else:
        natsql2sql_args.not_infer_group = True

    # 2. Prepare data
    tables = json.load(open(args.table_file,'r'))
    table_dict = dict()
    for t in tables:
        table_dict[t["db_id"]] = t
    sqls = json.load(open(args.natsql_file,"r"))
    
    with open(args.output_file, "w") as output_file:
        for i,sql in enumerate(sqls):
            if "pattern_tok" in sql:
                sq = SubQuestion(sql["question"],sql["question_type"],sql["table_match"],sql["question_tag"],sql["question_dep"],sql["question_entt"], sql, run_special_replace=False)
            else:
                sq = None
            try:
                query,_,__ = create_sql_from_natSQL(sql["NatSQL"], sql['db_id'], "data/database/"+sql['db_id']+"/"+sql['db_id']+".sqlite", table_dict[sql['db_id']], sq, remove_values=args.test_executable_natsql, remove_groupby_from_natsql=args.remove_groupby_from_natsql, args=natsql2sql_args)
            except:
                query = None
            if query is not None:
                output_file.write(query + '\n')
            else:
                output_file.write("NONE\n")
