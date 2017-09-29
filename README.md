# fortigate-scripts
## Copy config

This script gets the configuration from one fortigate and attempts to copy the configuration to another. 

Why not only restore from a file?

Short Story:

This was made because I was stupid enough to upgrade our fortigates to a buggy version without taking backup, and downgrading would result in losing configuration. So i downgraded one of the fortigates in HA, used this script to restore most of the configuration, failed over to the downgraded fortigate in order to downgrade the other.
