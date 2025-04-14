#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description='运行 FastAPI 应用测试')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细测试信息')
    parser.add_argument('--test', '-t', type=str, default=None,
                        help='运行特定测试，例如: test_ping')
    parser.add_argument('--cov', action='store_true',
                        help='生成测试覆盖率报告')
    return parser.parse_args()


def run_tests(args):
    cmd = ['pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    if args.test:
        cmd.append(f'test_app.py::{args.test}')
    
    if args.cov:
        cmd.extend(['--cov=app', '--cov-report=term', '--cov-report=html'])
    
    print(f"运行命令: {' '.join(cmd)}")
    return subprocess.call(cmd)


if __name__ == '__main__':
    args = parse_args()
    sys.exit(run_tests(args)) 