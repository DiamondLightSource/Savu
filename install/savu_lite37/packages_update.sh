#!/bin/bash
#title           :packages_update.sh
#description     :This script safely updates packages in Savu`s conda environment
#author          :Daniil Kazantsev
#date            :18.01.2021
#version         :0.1
#requirements    :installed Savu conda environment with all dependencies satisfied
#usage           :bash packages_update.sh branch_name

# Update strategy steps:
# 1. Use freshly created conda environment with Savu+dependencies using spec-file.txt
# 2. Using packages_to_update.txt file find a package to update and its stable (tests passed) and unstable (tests failed) versions.
# 3. Find the latest version of the package.
# 4. If the latest version is the same as the stable/unstable version, then continue to the NEXT package in the list. If the version
# is NEW then update it.
# 5. Install a new version of the package and run `savu_full_tests`
# 6  If the tests PASSS then mark a new version as STABLE in packages_update.txt if not then as UNSTABLE
# 7. Continue to the next package in the list
# 8. When the loop is finished generate a new explicit list file `conda list --explicit > spec-file.txt
# 9. replace all .conda file extentions with tar.bz2 e.g. sed -i 's/.conda/.tar.bz2/g' spec-file.txt

function version { echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }'; }

label="$1"
savu_version="4_0"
filename='packages_to_update.txt'
current_date=$(date '+%Y-%m-%d')
n=1
# Update each of the packages in a loop
while IFS="|" read -r package_name channel_name stable_version failed_version incompatable_version date ; do
  if [ "${package_name:0:1}" != "#" ]; then
  echo "--> The package $package_name has the STABLE version: $stable_version updated on $date" | xargs
  # search for associated versions of a package on conda cloud
  conda search -c $channel_name -f $package_name  > package_versions.file
  filename2='package_versions.file'
  # extract the latest version
  while IFS=$' \t\n' read -r name version build channel ; do
    eval "new_version_package$c=$version";
  done < $filename2
  echo "--> The latest version of the $package_name package is: $new_version_package" | xargs
  # Perform checks for the extracted latest version of the package
    if [ $(version $new_version_package) -ne $(version $stable_version) ]; then
      if [ $(version $new_version_package) > $(version $stable_version) ]; then
        if [ $(version $new_version_package) -ne $(version $failed_version) ]; then
          echo "--> Installing a NEW version of the package"
          conda install --yes -c $channel_name $package_name --force-reinstall --no-deps
          # Generate an explicit list file with installed conda packages
          conda list --explicit > spec-savu"$savu_version"_lite_"$label".txt
          sed -i 's/\.conda/.tar.bz2/g' spec-savu"$savu_version"_lite_"$label".txt
          echo "--> Check that the package is _actually_ updated"
          checkpack_var=$(grep $package_name spec-savu"$savu_version"_lite_"$label".txt)
          if [[ $checkpack_var == *"$new_version_package"* ]]; then
            echo "--> The package $package_name is truly updated to version $new_version_package continue with savu_full_tests" | xargs
            savu_full_tests  2>&1 | tee savu_full_tests_log.txt
            # grep OK variable in the output log
            VAR_PASS=$(grep "Tests PASSED" savu_full_tests_log.txt)
              if [ "$VAR_PASS" = "Tests PASSED" ]; then
                echo "--> Tests PASSED, update the STABLE version and the timestamp"
                sed -i -e "/$package_name/s/$stable_version/\ \ \ \ $new_version_package \ \ \ \ \ /" "$filename"
              else
                echo "--> Tests FAILED, update the FAILED version and the timestamp"
                sed -i -e "/$package_name/s/$failed_version/\ \ \ \ $new_version_package \ \ \ \ \ /" "$filename"
                echo "--> Downgrading the package to STABLE version"
                #conda uninstall $package_name
                # remove leading whitespace characters
                stable_version="${stable_version#"${stable_version%%[![:space:]]*}"}"
                # remove trailing whitespace characters
                stable_version="${stable_version%"${stable_version##*[![:space:]]}"}"
                package_name="${package_name#"${package_name%%[![:space:]]*}"}"
                # remove trailing whitespace characters
                package_name="${package_name%"${package_name##*[![:space:]]}"}"
                channel_name="${channel_name#"${channel_name%%[![:space:]]*}"}"
                # remove trailing whitespace characters
                channel_name="${channel_name%"${channel_name##*[![:space:]]}"}"
                conda install --yes -c $channel_name $package_name=$stable_version --force-reinstall --no-deps
              fi
          else
            echo "The package $package_name has NOT been updated to the NEW version $new_version_package succesfully, mark as INCOMPATIBLE" | xargs
            sed -i -e "/$package_name/s/$incompatable_version/\ \ \ \ $new_version_package \ \ \ \ \ /" "$filename"
          fi
          sed -i -e "/$package_name/s/$date/$current_date/" "$filename"
        else
          echo "--> The newer version marked as FAILED in the provided text file, no updating here"
        fi
      fi
    else
      echo "--> New version is the same as the STABLE one, continue to the next package"
    fi
  fi
n=$((n+1))
echo "**********************************************************************"
done < $filename
#
conda list --explicit > spec-savu"$savu_version"_lite_"$label".txt
sed -i 's/\.conda/.tar.bz2/g' spec-savu"$savu_version"_lite_"$label".txt
#clean up
rm -rf 0* 1* 2*
