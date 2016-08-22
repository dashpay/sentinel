    def get_prepare_command(self):
        methods = [
            'object_parent_hash',
            'object_revision',
            'object_creation_time',
            'object_name',
            'object_data'
        ]
        cmd = "gobject prepare %s %s %s %s %s" % [self.governance_object.__getattr__(field) for field in methods]
