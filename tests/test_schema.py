from common import *


class TestSchema(TestCase):
    
    def setUp(self):
                
        sg = Shotgun()
        self.sg = self.fix = fix = Fixture(sg)
        
        proj = fix.Project('Test Project ' + mini_uuid())
        seqs = [proj.Sequence(code, project=proj) for code in ('AA', 'BB')]
        shots = [seq.Shot('%s_%03d' % (seq['code'], i), project=proj) for seq in seqs for i in range(1, 3)]
        steps = [fix.find_or_create('Step', code=code, short_name=code) for code in ('Anm', 'Comp', 'Model')]
        tasks = [shot.Task(step['code'] + ' something', step=step, entity=shot, project=proj) for step in steps for shot in shots]
        
        self.proj = minimal(proj)
        self.seqs = map(minimal, seqs)
        self.shots = map(minimal, shots)
        self.steps = map(minimal, steps)
        self.tasks = map(minimal, tasks)

        self.session = Session(self.sg)
        self.sgfs = SGFS(root=self.sandbox, session=self.session)
    
    def test_graph_shape(self):
        
        schema = Schema('v1')
        schema.pprint()
        
        self.assertEqual(schema.entity_type, 'Project')
        self.assertEqual(len(schema.children), 2)
        
        asset = schema.children['Asset']
        self.assertEqual(asset.entity_type, 'Asset')
        self.assertEqual(len(asset.children), 1)
        
        atask = asset.children['Task']
        self.assertEqual(atask.entity_type, 'Task')
        self.assertEqual(len(atask.children), 0)
        
        seq = schema.children['Sequence']
        self.assertEqual(seq.entity_type, 'Sequence')
        self.assertEqual(len(seq.children), 1)
        
        shot = seq.children['Shot']
        self.assertEqual(shot.entity_type, 'Shot')
        self.assertEqual(len(shot.children), 1)
        
        stask = shot.children['Task']
        self.assertEqual(stask.entity_type, 'Task')
        self.assertEqual(len(stask.children), 0)

        