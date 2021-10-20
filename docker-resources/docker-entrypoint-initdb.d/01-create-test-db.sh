#!/bin/bash
set -e

influx -execute "CREATE DATABASE postgres_stats"
