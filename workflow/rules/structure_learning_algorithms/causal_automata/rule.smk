rule:
    """
    The variable module_name is determined from the folder name
    and set in the Snakefile.
    """
    name:
        module_name
    input:
        data = alg_input_data()
    output:
        adjmat = alg_output_adjmat_path(module_name),
        time = alg_output_time_path(module_name),
        ntests = alg_output_ntests_path(module_name)
    # Local development: keep container None and use the sibling env.yaml.
    # For an upstream contribution, build/push Dockerfile and set e.g.
    #   container: "docker://bpimages/causal_automata:0.3.1"
    container:
        None
    conda:
        "env.yaml"
    script:
        "script.py"
