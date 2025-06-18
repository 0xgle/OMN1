def generate_report(mode, targets, reqs, threads):
    with open("audit_report.txt", "w") as f:
        f.write("OMN1_CANNON REPORT\n")
        f.write(f"Mode: {mode}\nTargets: {targets}\nRequests: {reqs}\nThreads: {threads}\n")
