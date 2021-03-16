#!/bin/bash
#title           :metayaml_update.sh
#description     :This script updates meta.yaml for Savu-lite conda recipe based on provided explicit list file
#author          :Daniil Kazantsev
#date            :05.03.2021
#version         :0.1
#requirements    :meta.yaml amd savu3_0_lite.txt
#usage           :bash metayaml_update.sh meta.yaml savu3_0_lite.txt

meta_file="$1"  # meta.yaml file to update
explicit_file="$2"  # explicit packages list file
blankspace=" "
lineNumberIs=18
lineNumberIs2=5
while IFS="|" read -r line ; do
  # extract strings into variables from meta_file
  package_name="$(cut -d' ' -f6 <<<"$line")"
  version="$(cut -d' ' -f7 <<<"$line")"
  build_version="$(cut -d' ' -f8 <<<"$line")"
  # check that variable package_name is NOT empty
  if [ "$package_name" != "" ]; then
    line_to_replace_meta="$package_name$blankspace$version$blankspace$build_version"
    while IFS="|" read -r line_explicit_list ; do
      shortened_string=${line_explicit_list##*/}
      if [[ $package_name == "python" ]]; then
        package_name+="-3."
      fi
      if [[ $package_name == "numpy" ]]; then
        package_name+="-1."
      fi
      if [[ $package_name == "openmpi" ]]; then
        package_name+="-4."
      fi
      if [[ $package_name == "pytest" ]]; then
        package_name+="-6."
      fi
      if [[ $shortened_string =~ .*$package_name.* ]]; then
        # ready to initialise variables from the explicit list
        package_name_explicit_t="$(cut -d'.' -f1 <<<"$shortened_string")"
        package_name_explicit=${package_name_explicit_t%-*}
        version_explicit_t=${shortened_string%-*}
        version_explicit=${version_explicit_t##*-}
        build_version_t=${shortened_string##*-}
        build_version_explicit="$(cut -d'.' -f1 <<<"$build_version_t")"
        # form the line of the meta.yaml format, e.g.: "- python 3.7.5 h0371630_0"
        line_to_include_meta="$package_name_explicit$blankspace$version_explicit$blankspace$build_version_explicit"
      fi
    done < <(tail -n "+$lineNumberIs2" $explicit_file)
    # now relpace the items in meta.yaml file
    sed -i "s/\b$line_to_replace_meta\b/$line_to_include_meta/g" $meta_file
  fi
  if [ "${line}" == "test:" ]; then
    break
  fi
done < <(tail -n "+$lineNumberIs" $meta_file)
