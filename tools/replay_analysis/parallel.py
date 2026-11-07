"""Run independent model fits side by side on every processor core (the workspace has 2, GitHub's machines 4).

Fresh processes ("spawn"), not forked ones: forked workers deadlock once the parent has used the model library's
threads (found 2026-11-06). Inside a worker it runs serially (a worker can't start workers of its own). Results come
back in the order of the jobs, so a parallel run gives exactly what a serial one would.

In code: parallel.run(fn, jobs) -> [fn(job) for job in jobs], side by side when it helps. fn must be a top-level
function of an importable module."""
import multiprocessing as mp
import os

CORES = int(os.environ.get("GVG_CORES") or os.cpu_count() or 1)


def run(fn, jobs):
    jobs = list(jobs)
    if len(jobs) < 2 or CORES < 2 or mp.current_process().daemon:
        return [fn(j) for j in jobs]
    with mp.get_context("spawn").Pool(min(CORES, len(jobs))) as p:
        return p.map(fn, jobs, chunksize=1)
