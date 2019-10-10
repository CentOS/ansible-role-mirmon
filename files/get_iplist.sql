SELECT DISTINCT ip FROM mirrors m, ipaddresses ip WHERE m.mirror_id=ip.mirror_id AND status IN ('Active', 'Master') AND (expires IS NULL OR expires >= NOW()) UNION SELECT DISTINCT ip FROM ipaddresses WHERE mirror_id IS NULL AND (expires IS NULL OR expires >= NOW())