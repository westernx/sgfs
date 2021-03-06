from subprocess import call
import os

from common import *


class TestCache(TestCase):
    
    def setUp(self):
        sg = Shotgun()
        self.sg = self.fix = fix = Fixture(sg)
    
    def test_lookup_paths(self):
        
        sgfs = SGFS(root=self.sandbox, shotgun=self.sg)
        proj = sgfs.session.merge(self.fix.Project('Test Project ' + mini_uuid()))        
        sgfs.create_structure(proj, allow_project=True)
        cache = sgfs.path_cache(proj)
        
        root = os.path.abspath(os.path.join(self.sandbox, proj['name'].replace(' ', '_')))
        
        self.assertEqual(1, len(cache))
        self.assertEqual(cache.get(proj), root)
        
        stat = os.stat(os.path.join(root, '.sgfs/cache.sqlite'))
        print oct(stat.st_mode)
        self.assertEqual(stat.st_mode & 0777, 0666)
    
    def test_assert_tag_exists(self):
        
        sgfs = SGFS(root=self.sandbox, shotgun=self.sg)
        proj = sgfs.session.merge(self.fix.Project('Test Project ' + mini_uuid()))        
        sgfs.create_structure(proj, allow_project=True)
        cache = sgfs.path_cache(proj)
        
        root = os.path.abspath(os.path.join(self.sandbox, proj['name'].replace(' ', '_')))
        os.unlink(os.path.join(root, '.sgfs.yml'))
        
        self.assertEqual(1, len(cache)) # This is still wierd, but expected.
        with capture_logs(silent=True) as logs:
            self.assertEqual(cache.get(proj), None)
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].levelname, 'WARNING')

        stat = os.stat(os.path.join(root, '.sgfs/cache.sqlite'))
        print oct(stat.st_mode)
        self.assertEqual(stat.st_mode & 0777, 0666)

    def test_old_cache_location(self):
        
        sgfs = SGFS(root=self.sandbox, shotgun=self.sg)
        proj = sgfs.session.merge(self.fix.Project('Test Project ' + mini_uuid()))        
        sgfs.create_structure(proj, allow_project=True)

        root = os.path.abspath(os.path.join(self.sandbox, proj['name'].replace(' ', '_')))
        call(['mv', 
            os.path.join(root, '.sgfs/cache.sqlite'),
            os.path.join(root, '.sgfs-cache.sqlite'),
        ])

        cache = sgfs.path_cache(proj)
        
        self.assertEqual(1, len(cache))
        self.assertEqual(cache.get(proj), root)
        
        
