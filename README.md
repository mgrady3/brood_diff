# Brood_diff is a CLI for calculating the diff between two given brood indices.

### Use case

A client has a local Brood instance running on an air-gapped network behind
their corporate firewall. Thus their Brood instance is unable to use the
built-in sync feature to sync with the Enthought production Brood instance.

Currently there is no simple method for calculating which packages need to 
added to the client's Brood in order to bring their Brood in-sync with the
Enthought Brood. The old method is to simply do a full export/import cycle
of the Enthought Brood, however this is time consuming and requires the
transfer of potentially many 10's of Gb of data when only a small handful of
data actually needs to be uploaded to the client's server.

Brood_diff provides a CLI method of calculating the difference between two
given brood indices represented in JSON.


### Usage:

* Get Index: Use this function to generate the json representation of a brood index

    ```
    python diff.py get-index -u <brood-url>
                             -r <org/repo>
                             -p <platform>
                             -v <python-tag>
                             -o <path-to-output-file>
    ```

* Index Diff: Use this function to calculate the difference between two brood indices.

    ```
    python diff.py gen-diff -l <path-to-local-index>
                            -r <path-to-remote-index>
                            -o <path-to-output-file>
    ```

### Notes

Repositories are specified in the Brood/Hatcher format <org/repo> e.g. to
select the Enthought free repository : -r enthought/free.

Currently the diff calculates only missing eggs. The reasoning behind this is
that we should avoid making changes to the end-user's Brood that may break
code they they have written. Thus no deleted eggs or moved eggs are calculated.

