import porespy as ps
import numpy as np
import scipy.spatial as sptl
import scipy.ndimage as spim
import matplotlib.pyplot as plt
import pytest
from edt import edt


class ToolsTest():
    
    def setup_class(self):
        plt.close('all')
        self.im = np.random.randint(0, 10, 20)
        np.random.seed(0)
        self.blobs = ps.generators.blobs(shape=[101, 101])
        self.im2D = ps.generators.blobs(shape=[51, 51])
        self.im3D = ps.generators.blobs(shape=[51, 51, 51])
        self.labels, N = spim.label(input=self.blobs)

    def test_unpad(self):
        pad_width = [10, 20]
        im = ps.generators.blobs([200, 300], porosity=0.3)
        im1 = np.pad(im, pad_width, mode="constant", constant_values=1)
        im2 = ps.tools.unpad(im1, pad_width)
        assert np.all(im == im2)

    def test_unpad_int_padwidth(self):
        pad_width = 10
        im = ps.generators.blobs([200, 300], porosity=0.3)
        im1 = np.pad(im, pad_width, mode="constant", constant_values=1)
        im2 = ps.tools.unpad(im1, pad_width)
        assert np.all(im == im2)

    def test_unpad_different_padwidths_on_each_axis(self):
        pad_width = [[10, 20], [30, 40]]
        im = ps.generators.blobs([200, 300], porosity=0.3)
        im1 = np.pad(im, pad_width, mode="constant", constant_values=1)
        im2 = ps.tools.unpad(im1, pad_width)
        assert np.all(im == im2)

    def test_randomize_colors(self):
        randomized_im = ps.tools.randomize_colors(im=self.im)
        assert np.unique(self.im).size == np.unique(randomized_im).size
        assert np.all(np.unique(self.im) == np.unique(randomized_im))

    def test_make_contiguous_size(self):
        cont_im = ps.tools.make_contiguous(self.im)
        assert np.unique(self.im).size == np.unique(cont_im).size

    def test_make_contiguous_contiguity(self):
        cont_im = ps.tools.make_contiguous(self.im)
        assert np.all(np.arange(np.unique(self.im).size) == np.unique(cont_im))

    def test_make_contiguous_w_negs_and_modes(self):
        im = np.array([[0, 0, 1, 3], [-2, -4, 1, 3], [-4, 3, 5, 0]])
        a = ps.tools.make_contiguous(im, mode='keep_zeros').flatten()
        assert np.all(a == [0, 0, 3, 4, 2, 1, 3, 4, 1, 4, 5, 0])
        b = ps.tools.make_contiguous(im, mode='clipped').flatten()
        assert np.all(b == [0, 0, 1, 2, 0, 0, 1, 2, 0, 2, 3, 0])
        c = ps.tools.make_contiguous(im, mode='symmetric').flatten()
        assert np.all(c == [0, 0, 1, 2, -1, -2, 1, 2, -2, 2, 3, 0])
        d = ps.tools.make_contiguous(im, mode='none').flatten()
        assert np.all(d == [3, 3, 4, 5, 2, 1, 4, 5, 1, 5, 6, 3])

    def test_extract_subsection(self):
        sec = ps.tools.extract_subsection(self.blobs, [0.5])
        assert np.all(np.array(np.shape(sec)) == 50)

    def test_extract_cylinder(self):
        im = np.ones([200, 300, 400], dtype=bool)
        cx = ps.tools.extract_cylinder(im)
        assert cx.sum() == 14132200
        cy = ps.tools.extract_cylinder(im, axis=1)
        assert cy.sum() == 9419100
        cz = ps.tools.extract_cylinder(im, axis=2)
        assert cz.sum() == 12558800
        cr = ps.tools.extract_cylinder(im, r=100)
        assert cr.sum() == 6279400

    def test_bbox_to_slices(self):
        s = ps.tools.bbox_to_slices([0, 0, 0, 10, 10, 10])
        assert np.all(self.im3D[s].shape == (10, 10, 10))

    def test_get_planes(self):
        x, y, z = ps.tools.get_planes(self.im3D)
        assert np.all(x.shape == (51, 51))
        assert np.all(y.shape == (51, 51))
        assert np.all(z.shape == (51, 51))
        with pytest.raises(ValueError):
            ps.tools.get_planes(self.im2D)

    def test_get_planes_not_squeezed(self):
        x, y, z = ps.tools.get_planes(self.im3D, squeeze=False)
        assert np.all(x.shape == (1, 51, 51))
        assert np.all(y.shape == (51, 1, 51))
        assert np.all(z.shape == (51, 51, 1))

    def test_get_border(self):
        c = ps.tools.get_border(self.im2D.shape, thickness=1, mode='corners')
        assert c.sum() == 4
        c = ps.tools.get_border(self.im3D.shape, thickness=1, mode='corners')
        assert c.sum() == 8
        c = ps.tools.get_border(self.im2D.shape, thickness=1, mode='edges')
        assert c.sum() == 200
        c = ps.tools.get_border(self.im3D.shape, thickness=1, mode='edges')
        assert c.sum() == 596
        c = ps.tools.get_border(self.im2D.shape, thickness=1, mode='faces')
        assert c.sum() == 200
        c = ps.tools.get_border(self.im3D.shape, thickness=1, mode='faces')
        assert c.sum() == 15002

    def test_align_image_w_openpnm(self):
        im = ps.tools.align_image_with_openpnm(np.ones([40, 50]))
        assert im.shape == (50, 40)
        im = ps.tools.align_image_with_openpnm(np.ones([40, 50, 60]))
        assert im.shape == (60, 50, 40)

    def test_inhull(self):
        X = np.random.rand(25, 2)
        hull = sptl.ConvexHull(X)
        assert not ps.tools.in_hull([[0, 0]], hull)
        assert ps.tools.in_hull([np.mean(X, axis=0)], hull)
        X = np.random.rand(25, 3)
        hull = sptl.ConvexHull(X)
        assert not ps.tools.in_hull([[0, 0, 0]], hull)
        assert ps.tools.in_hull([np.mean(X, axis=0)], hull)

    def test_insert_sphere_2D_no_overwrite(self):
        im = np.zeros(shape=[200, 200], dtype=bool)
        im = ps.tools.insert_sphere(im, c=[100, 100], r=50, v=1, overwrite=False)
        im = ps.tools.insert_sphere(im, c=[110, 100], r=50, v=2, overwrite=False)
        im = ps.tools.insert_sphere(im, c=[90, 100], r=50, v=3, overwrite=False)
        vals, counts = np.unique(im, return_counts=True)
        assert np.all(np.unique(im) == vals)
        assert counts[1] > counts[2]

    def test_insert_sphere_2D_w_overwrite(self):
        im = np.zeros(shape=[200, 200], dtype=bool)
        im = ps.tools.insert_sphere(im, c=[100, 100], r=50, v=1, overwrite=True)
        im = ps.tools.insert_sphere(im, c=[110, 100], r=50, v=2, overwrite=True)
        im = ps.tools.insert_sphere(im, c=[90, 100], r=50, v=3, overwrite=True)
        vals, counts = np.unique(im, return_counts=True)
        assert np.all(np.unique(im) == vals)
        assert counts[1] < counts[2]

    def test_insert_sphere_3D_no_overwrite(self):
        im = np.zeros(shape=[200, 200, 200], dtype=bool)
        im = ps.tools.insert_sphere(im, c=[100, 100, 100], r=50, v=1,
                                    overwrite=False)
        im = ps.tools.insert_sphere(im, c=[110, 100, 100], r=50, v=2,
                                    overwrite=False)
        im = ps.tools.insert_sphere(im, c=[90, 100, 100], r=50, v=3,
                                    overwrite=False)
        vals, counts = np.unique(im, return_counts=True)
        assert np.all(np.unique(im) == vals)
        assert counts[1] > counts[2]

    def test_insert_sphere_3D_w_overwrite(self):
        im = np.zeros(shape=[200, 200, 200], dtype=bool)
        im = ps.tools.insert_sphere(im, c=[100, 100, 100], r=50, v=1,
                                    overwrite=True)
        im = ps.tools.insert_sphere(im, c=[110, 100, 100], r=50, v=2,
                                    overwrite=True)
        im = ps.tools.insert_sphere(im, c=[90, 100, 100], r=50, v=3,
                                    overwrite=True)
        vals, counts = np.unique(im, return_counts=True)
        assert np.all(np.unique(im) == vals)
        assert counts[1] < counts[2]

    def test_subdivide_2D_with_scalar_overlap(self):
        im = np.ones([150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=10)
        assert np.all(im[s[0][0]].shape == (60, 60))
        assert np.all(im[s[0][1]].shape == (60, 70))
        assert np.all(im[s[1][1]].shape == (70, 70))

    def test_subdivide_2D_with_vector_overlap(self):
        im = np.ones([150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=[10, 20])
        assert np.all(im[s[0][0]].shape == (60, 70))
        assert np.all(im[s[0][1]].shape == (60, 90))
        assert np.all(im[s[1][1]].shape == (70, 90))

    def test_subdivide_2D_with_scalar_overlap_flattened(self):
        im = np.ones([150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=10, flatten=True)
        assert np.all(im[s[0]].shape == (60, 60))
        assert np.all(im[s[1]].shape == (60, 70))
        assert np.all(im[s[4]].shape == (70, 70))

    def test_subdivide_2D_with_vector_overlap_flattened(self):
        im = np.ones([150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=[10, 20], flatten=True)
        assert np.all(im[s[0]].shape == (60, 70))
        assert np.all(im[s[1]].shape == (60, 90))
        assert np.all(im[s[4]].shape == (70, 90))

    def test_subdivide_3D_with_scalar_overlap(self):
        im = np.ones([150, 150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=10)
        assert np.all(im[s[0][0][0]].shape == (60, 60, 60))
        assert np.all(im[s[0][0][1]].shape == (60, 60, 70))
        assert np.all(im[s[1][1][1]].shape == (70, 70, 70))

    def test_subdivide_3D_with_vector_overlap(self):
        im = np.ones([150, 150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=[10, 20, 30])
        assert np.all(im[s[0][0][0]].shape == (60, 70, 80))
        assert np.all(im[s[0][0][1]].shape == (60, 70, 110))
        assert np.all(im[s[1][1][1]].shape == (70, 90, 110))

    def test_subdivide_3D_with_scalar_overlap_flattened(self):
        im = np.ones([150, 150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=10, flatten=True)
        assert np.all(im[s[0]].shape == (60, 60, 60))
        assert np.all(im[s[1]].shape == (60, 60, 70))
        assert np.all(im[s[13]].shape == (70, 70, 70))

    def test_subdivide_3D_with_vector_overlap_flattened(self):
        im = np.ones([150, 150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=[10, 20, 30], flatten=True)
        assert np.all(im[s[0]].shape == (60, 70, 80))
        assert np.all(im[s[1]].shape == (60, 70, 110))
        assert np.all(im[s[13]].shape == (70, 90, 110))

    def test_subdivided_shape_flattened(self):
        im = np.ones([150, 150, 150])
        s = ps.tools.subdivide(im, divs=3, overlap=[10, 20, 30], flatten=True)
        assert np.all(len(s) == 27)

    def test_subdivided_shape_not_flattened(self):
        im = np.ones([160, 160, 160])
        s = ps.tools.subdivide(im, divs=4, overlap=[10, 20, 30], flatten=False)
        assert len(s[0]) == 4
        assert len(s[0][0]) == 4
        assert len(s[0][0][0]) == 3

    def test_size_to_seq(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        nsizes = np.size(np.unique(sz))
        sq = ps.tools.size_to_seq(sz)
        nsteps = np.size(np.unique(sq))
        assert nsteps == nsizes

    def test_size_to_seq_int_bins(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        sq = ps.tools.size_to_seq(sz, bins=5)
        nsteps = np.size(np.unique(sq))
        assert nsteps == 5

    def test_size_to_seq_too_many_bins(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        sq = ps.tools.size_to_seq(sz, bins=20)
        nsteps = np.size(np.unique(sq))
        assert nsteps < 20

    def test_seq_to_satn_fully_filled(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        sq = ps.tools.size_to_seq(sz)
        sat = ps.tools.seq_to_satn(sq)
        assert sat.max() == 1

    def test_seq_to_satn_partially_filled(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        sq = ps.tools.size_to_seq(sz)
        sq[sq == sq.max()] = -1
        sat = ps.tools.seq_to_satn(sq)
        assert sat.max() < 1

    def test_size_to_satn(self):
        im = self.im2D
        sz = ps.filters.porosimetry(im)
        satn = ps.tools.size_to_satn(sz)
        assert satn.max() == 1.0
        satn = ps.tools.size_to_satn(sz, bins=4)
        assert satn.max() == 1.0

    def test_compare_size_and_seq_to_satn(self):
        im = ps.generators.blobs(shape=[250, 250])
        dt = edt(im)
        sizes = np.arange(int(dt.max())+1, 0, -1)
        mio = ps.filters.porosimetry(im, sizes=sizes)
        mio_satn = ps.tools.size_to_satn(size=mio, im=im)
        mio_seq = ps.tools.size_to_seq(mio)
        mio_seq[im*(mio_seq == 0)] = -1  # Adjust to set uninvaded to -1
        mio_satn_2 = ps.tools.seq_to_satn(mio_seq)
        assert np.all(mio_satn == mio_satn_2)

    def test_zero_coners(self):
        im = np.arange(1, 16).reshape(3, 5)
        desired = np.array([[1, 2, 3, 4, 5],
                            [0, 7, 0, 0, 0],
                            [0, 12, 0, 0, 0]])
        im1 = im.copy()
        ps.tools.zero_corners(im1, [[0, 2], [1, 3]])
        np.testing.assert_allclose(im1, desired)

        with pytest.raises(Exception):
            im2 = im.copy()
            ps.tools.zero_corners(im2, [[0, 2], [1, 3], [0, 0]])

        with pytest.raises(Exception):
            im2 = im.copy()
            ps.tools.zero_corners(im2, [[0, 2], [1, 3, 3]])

        desired = np.array([[0, 2, 3, 4, 0],
                            [6, 7, 8, 9, 10],
                            [0, 12, 13, 14, 0]])
        im3 = im.copy()
        ps.tools.zero_corners(im3, 1)
        np.testing.assert_allclose(im3, desired)

    def test_sanitize_filename(self):
        fname = "test.stl.stl"
        assert ps.tools.sanitize_filename(fname, "stl") == "test.stl.stl"
        assert ps.tools.sanitize_filename(fname, "vtk") == "test.stl.stl.vtk"
        assert ps.tools.sanitize_filename(fname, "stl", exclude_ext=True) == "test.stl"
        
    def test_extract_regions(self):
        im = spim.label(self.im2D)[0]
        im = im*ps.tools.extract_regions(im, labels=[2, 3], trim=False)
        assert np.all(np.unique(im) == [0, 2, 3])
        
    def test_marching_map(self):
        im = ps.generators.lattice_spheres(shape=[107, 107],
                                           radius=5, offset=9,
                                           lattice='tri')
        im = im[5:102, 5:102]
        bd = np.zeros_like(im)
        bd[:, 0] = True
        from porespy.tools import marching_map
        # At present scikit-fmm is not installed with porespy, however,
        # when we switch to conda install, we can include it in our requirements
        # at which point this test will no longer raise an exception and fail
        with pytest.raises(Exception):
            fmm = marching_map(path=im, start=bd)

    def test_ps_strels(self):
        c = ps.tools.ps_disk(r=3)
        assert c.sum() == 25
        c = ps.tools.ps_disk(r=3, smooth=False)
        assert c.sum() == 29
        b = ps.tools.ps_ball(r=3)
        assert b.sum() == 93
        b = ps.tools.ps_ball(r=3, smooth=False)
        assert b.sum() == 123
        s = ps.tools.ps_rect(w=3, ndim=2)
        assert s.sum() == 9
        c = ps.tools.ps_rect(w=3, ndim=3)
        assert c.sum() == 27

    def test_find_outer_region(self):
        outer = ps.tools.find_outer_region(self.im3D)
        assert outer.sum() == 1989
        outer = ps.tools.find_outer_region(self.im2D)
        assert outer.sum() == 64


if __name__ == '__main__':
    t = ToolsTest()
    self = t
    t.setup_class()
    for item in t.__dir__():
        if item.startswith('test'):
            print(f"Running test: {item}")
            t.__getattribute__(item)()
