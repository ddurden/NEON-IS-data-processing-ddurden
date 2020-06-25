#!/usr/bin/env python3
import environs
import cx_Oracle
from contextlib import closing

from water_quality_cloning.named_location_creator import NamedLocationCreator
from water_quality_cloning.active_period_assigner import ActivePeriodAssigner
from water_quality_cloning.asset_assigner import AssetAssigner
from water_quality_cloning.geo_location_assigner import GeoLocationAssigner
from water_quality_cloning.location_tree_assigner import LocationTreeAssigner


def main():
    """
    Create new named locations by cloning the Water Quality-related aquatic PRT named locations
    and assign the same active periods, the same named location tree parent, the same geo-location, and assign those
    assets (sensors) currently redundantly assigned to the PRT named location to the cloned named locations.
    """
    clone_count = 0
    s1_location_count = 0
    s2_location_count = 0
    s1_clone_count = 0
    s2_clone_count = 0
    not_used_count = 0

    env = environs.Env()
    db_url = env.str('DATABASE_URL')
    with closing(cx_Oracle.connect(db_url)) as connection:

        named_location_creator = NamedLocationCreator(connection)
        active_period_assigner = ActivePeriodAssigner(connection)
        asset_assigner = AssetAssigner(connection)
        geo_location_assigner = GeoLocationAssigner(connection)
        location_tree_assigner = LocationTreeAssigner(connection)

        named_location_ids = named_location_creator.get_prt_wq_named_locations()
        for named_location_id in named_location_ids:
            named_location = named_location_creator.get_named_location(named_location_id)
            description = named_location.get('description')
            site = named_location.get('site')
            print(f'Site: "{site}", Description: "{description}"')
            if 'Not Used' in description:
                print(f'Not Used in description, location skipped.')
                not_used_count += 1
            else:
                if 'S1' in description and site != 'HOPB':
                    s1_location_count += 1
                    clones = []
                    for index in range(0, 6):
                        clone = named_location_creator.create_clone(named_location, clone_count)
                        clone_id = named_location_creator.save_clone(clone)
                        clone.update({'key': clone_id})
                        clones.append(clone)
                        clone_count += 1
                        active_period_assigner.assign_active_periods(named_location_id, clone_id)
                        location_tree_assigner.assign_to_same_parent(named_location_id, clone_id)
                        geo_location_assigner.assign_locations(named_location_id, clone_id)
                        s1_clone_count += 1
                    asset_assigner.assign_assets(named_location_id, clones)
                    clones.clear()
                if 'S2' in description or site == 'HOPB':
                    s2_location_count += 1
                    clones = []
                    for index in range(0, 7):  # clone S2 locations 7 times (for FDOM)
                        clone = named_location_creator.create_clone(named_location, clone_count)
                        clone_id = named_location_creator.save_clone(clone)
                        clone.update({'key': clone_id})
                        clones.append(clone)
                        clone_count += 1
                        active_period_assigner.assign_active_periods(named_location_id, clone_id)
                        location_tree_assigner.assign_to_same_parent(named_location_id, clone_id)
                        geo_location_assigner.assign_locations(named_location_id, clone_id)
                        s2_clone_count += 1
                    asset_assigner.assign_assets(named_location_id, clones)
                    clones.clear()
    print(f'S1 locations: {s1_location_count} ')
    print(f'Expected S1 clones ({s1_location_count} * 6): {s1_location_count * 6}')
    print(f'S2 locations: {s2_location_count}')
    print(f'Expected S2 clones ({s2_location_count} * 7): {s2_location_count * 7}')
    print(f'Expected {s1_clone_count} + {s2_clone_count} = {s1_clone_count + s2_clone_count} clones.')
    print(f'Created {clone_count} clones.')
    print(f'Locations containing not used in description: {not_used_count}')


if __name__ == "__main__":
    main()
