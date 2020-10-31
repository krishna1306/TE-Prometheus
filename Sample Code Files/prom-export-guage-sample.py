#!/usr/bin/env python
# coding: utf-8

import prometheus_client as prom



guages = {}

guages["latency"] = prom.Gauge('latency_total','Gauge latency figure', ["srcAgent", "dstAgentId", "srcAgentLocation", "dstAgentLocation", "version", "domain"])



guages["latency"].labels(srcAgent="123", dstAgentId="789", domain="GIS", version="1.0", srcAgentLocation="Bangkok", dstAgentLocation="Tokyo").set(13.45)




output = prom.exposition.generate_latest().decode("utf-8")


print(output)

