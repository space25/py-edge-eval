#!/usr/bin/env python3

import argparse

from pyEdgeEval.evaluators.cityscapes import CityscapesEvaluator


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate Cityscapes output")
    parser.add_argument(
        "cityscapes_path", type=str, help="the root path of the cityscapes dataset",
    )
    parser.add_argument(
        "pred_path", type=str, help="the root path of the predictions",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="the root path of where the results are populated",
    )
    parser.add_argument(
        "--categories",
        type=str,
        default="[1, 14]",
        help="the category number to evaluate; can be multiple values'[1, 14]'",
    )
    parser.add_argument(
        "--pre-seal",
        action="store_true",
        help="prior to SEAL, the evaluations were not as strict",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.5,
        help="scale of the data for evaluations",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="option to remove the thinning process (i.e. uses raw predition)",
    )
    parser.add_argument(
        "--apply-nms",
        action="store_true",
        help="applies NMS before evaluation",
    )
    parser.add_argument(
        "--thresholds",
        type=str,
        default="99",
        help="the number of thresholds (could be a list of floats); use 99 for eval",
    )
    parser.add_argument(
        "--nproc",
        type=int,
        default=4,
        help="the number of parallel threads",
    )

    return parser.parse_args()


def evaluate_cityscapes(
    cityscapes_path: str,
    pred_path: str,
    output_path: str,
    categories: str,
    pre_seal: bool,
    scale: float,
    apply_thinning: bool,
    apply_nms: bool,
    thresholds: str,
    nproc: int,
):
    """Evaluate Cityscapes"""

    # string evaluation for categories
    categories = categories.strip()
    try:
        categories = [int(categories)]
    except ValueError:
        try:
            if categories.startswith("[") and categories.endswith("]"):
                categories = categories[1:-1]
                categories = [int(cat.strip()) for cat in categories.split(",")]
            else:
                print(
                    "Bad categories format; should be a python list of floats (`[a, b, c]`)"
                )
                return
        except ValueError:
            print(
                "Bad categories format; should be a python list of ints (`[a, b, c]`)"
            )
            return

    for cat in categories:
        assert 0 < cat < 20, f"category needs to be between 1 ~ 19, but got {cat}"

    # string evaluation for thresholds
    thresholds = thresholds.strip()
    try:
        n_thresholds = int(thresholds)
        thresholds = n_thresholds
    except ValueError:
        try:
            if thresholds.startswith("[") and thresholds.endswith("]"):
                thresholds = thresholds[1:-1]
                thresholds = [float(t.strip()) for t in thresholds.split(",")]
            else:
                print(
                    "Bad threshold format; should be a python list of floats (`[a, b, c]`)"
                )
                return
        except ValueError:
            print(
                "Bad threshold format; should be a python list of ints (`[a, b, c]`)"
            )
            return

    # initialize evaluator
    evaluator = CityscapesEvaluator(
        dataset_root=cityscapes_path,
        pred_root=pred_path,
    )
    if evaluator.sample_names is None:
        # load custom sample names
        evaluator.set_sample_names()

    # set parameters
    # evaluator.set_pred_suffix("_leftImg8bit.png")  # potato save them using .png
    eval_mode = "pre-seal" if pre_seal else "post-seal"
    evaluator.set_eval_params(
        eval_mode=eval_mode,
        scale=scale,
        apply_thinning=apply_thinning,
        apply_nms=apply_nms,
    )

    # evaluate
    evaluator.evaluate(
        categories=categories,
        thresholds=thresholds,
        nproc=nproc,
        save_dir=output_path,
    )


def main():
    args = parse_args()

    apply_thinning = not args.raw

    evaluate_cityscapes(
        cityscapes_path=args.cityscapes_path,
        pred_path=args.pred_path,
        output_path=args.output_path,
        categories=args.categories,
        pre_seal=args.pre_seal,
        scale=args.scale,
        apply_thinning=apply_thinning,
        apply_nms=args.apply_nms,
        thresholds=args.thresholds,
        nproc=args.nproc,
    )


if __name__ == "__main__":
    main()
