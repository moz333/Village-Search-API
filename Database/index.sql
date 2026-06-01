--indexes
CREATE index idx_state_name on state(name);
CREATE index idx_district_name on district(name);
CREATE index idx_sub_district_name on sub_district(name);
CREATE index idx_village_name on village(name);

CREATE index idx_district_state on district(state_id);
CREATE index idx_subdistrict_district on sub_district(district_id);
CREATE index idx_village_subdistrict on village(sub_district_id);