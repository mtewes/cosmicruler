
SELECT `random_index`, `true_redshift_gal`, `logf_halpha_model1_ext`, `logf_halpha_model3_ext`, `euclid_nisp_h`, `euclid_vis` 
FROM flagship_mock_1_5_2_s 
TABLESAMPLE (BUCKET 1 OUT OF 256)

--> 2614.fits
