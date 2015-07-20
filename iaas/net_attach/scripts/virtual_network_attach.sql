DROP TABLE IF EXISTS virtual_network_attach;
CREATE TABLE IF NOT EXISTS virtual_network_attach (
    oid INT UNSIGNED NOT NULL AUTO_INCREMENT,
    vid INT UNSIGNED ,
    ssh_port INT UNSIGNED,
    ipv6 VARCHAR(255),
    used INT UNSIGNED,
    dns VARCHAR(255),
    ip VARCHAR(255),
    inner_port INT UNSIGNED,
    PRIMARY KEY (oid)
);


