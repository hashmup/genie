#!/bin/sh

./configure --prefix=$(cd ../; pwd)/exec/ \
  {% for option in options %}
  {{ option }} \
  {% endfor %}
  {% for key in compile_options %}
  {{ key }}={{ compile_options[key] }} \
  {% endfor %}
