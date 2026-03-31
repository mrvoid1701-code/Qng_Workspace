# G16b-v2 Candidate Evaluation (v1)

- mode: `prereg`
- generated_utc: `2026-03-01T23:51:46.258703Z`
- profiles: `1500`
- g16b_v1_fail: `344`
- g16b_v2_fail: `293`
- g16b_v2_pass: `1207`
- v1_fail_to_v2_pass: `110`
- v1_pass_to_v2_fail: `59`

## Pre-Registered Decision

- promotion target: `600/600 pass` (DS-002/003/006 x seeds 3401..3600)
- observed g16b-v2 pass: `1207/600`
- conclusion: `NOT ELIGIBLE FOR PROMOTION` (candidate-only remains)

## Dataset Summary

| dataset | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| DS-002 | 500 | 102 | 106 | 24 | 28 |
| DS-003 | 500 | 125 | 128 | 11 | 14 |
| DS-006 | 500 | 117 | 59 | 75 | 17 |

## Signal-Regime Breakdown

| low_signal | n | v1_fail | v2_fail | improved | degraded |
| --- | --- | --- | --- | --- | --- |
| true | 538 | 145 | 35 | 110 | 0 |
| false | 962 | 199 | 258 | 0 | 59 |

## Changed Decisions

| dataset | seed | v1 | v2 | branch | low_signal | r2_full | r2_high_signal | |pearson_hs| | |spearman_hs| |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-002 | 3605 | pass | fail | full_signal | false | 0.092951 | 0.495514 | 0.703927 | 0.704990 |
| DS-002 | 3607 | fail | pass | high_signal | true | 0.028173 | 0.140413 | 0.374717 | 0.353178 |
| DS-002 | 3609 | fail | pass | high_signal | true | 0.032204 | 0.130132 | 0.360738 | 0.259809 |
| DS-002 | 3610 | pass | fail | full_signal | false | 0.073763 | 0.366201 | 0.605146 | 0.569925 |
| DS-002 | 3613 | pass | fail | full_signal | false | 0.060247 | 0.164094 | 0.405085 | 0.323172 |
| DS-002 | 3621 | fail | pass | high_signal | true | 0.024908 | 0.088942 | 0.298232 | 0.361791 |
| DS-002 | 3626 | pass | fail | full_signal | false | 0.051966 | 0.123791 | 0.351839 | 0.347915 |
| DS-002 | 3627 | pass | fail | full_signal | false | 0.066631 | 0.203335 | 0.450927 | 0.410800 |
| DS-002 | 3636 | pass | fail | full_signal | false | 0.054113 | 0.182531 | 0.427236 | 0.349624 |
| DS-002 | 3654 | pass | fail | full_signal | false | 0.065255 | 0.252791 | 0.502784 | 0.481408 |
| DS-002 | 3671 | fail | pass | high_signal | true | 0.037960 | 0.180711 | 0.425101 | 0.414224 |
| DS-002 | 3672 | pass | fail | full_signal | false | 0.065366 | 0.260715 | 0.510603 | 0.462474 |
| DS-002 | 3678 | pass | fail | full_signal | false | 0.051002 | 0.134205 | 0.366339 | 0.374094 |
| DS-002 | 3690 | pass | fail | full_signal | false | 0.060693 | 0.198304 | 0.445314 | 0.515448 |
| DS-002 | 3702 | pass | fail | full_signal | false | 0.060510 | 0.269625 | 0.519255 | 0.505878 |
| DS-002 | 3717 | fail | pass | high_signal | true | 0.045717 | 0.107295 | 0.327560 | 0.359672 |
| DS-002 | 3727 | fail | pass | high_signal | true | 0.046936 | 0.162756 | 0.403431 | 0.391866 |
| DS-002 | 3746 | pass | fail | full_signal | false | 0.058578 | 0.240936 | 0.490852 | 0.437799 |
| DS-002 | 3754 | fail | pass | high_signal | true | 0.035261 | 0.248026 | 0.498022 | 0.472454 |
| DS-002 | 3759 | fail | pass | high_signal | true | 0.047117 | 0.141947 | 0.376759 | 0.479084 |
| DS-002 | 3768 | fail | pass | high_signal | true | 0.036552 | 0.078659 | 0.280462 | 0.397813 |
| DS-002 | 3777 | pass | fail | full_signal | false | 0.063041 | 0.197488 | 0.444396 | 0.337731 |
| DS-002 | 3789 | pass | fail | full_signal | false | 0.077816 | 0.295441 | 0.543545 | 0.617293 |
| DS-002 | 3797 | fail | pass | high_signal | true | 0.046597 | 0.182074 | 0.426701 | 0.450649 |
| DS-002 | 3798 | fail | pass | high_signal | true | 0.022831 | 0.091662 | 0.302758 | 0.642242 |
| DS-002 | 3799 | pass | fail | full_signal | false | 0.054308 | 0.258990 | 0.508910 | 0.539029 |
| DS-002 | 3823 | pass | fail | full_signal | false | 0.056789 | 0.202253 | 0.449725 | 0.230759 |
| DS-002 | 3826 | fail | pass | high_signal | true | 0.033928 | 0.117519 | 0.342811 | 0.285851 |
| DS-002 | 3829 | fail | pass | high_signal | true | 0.049622 | 0.165654 | 0.407007 | 0.415243 |
| DS-002 | 3832 | pass | fail | full_signal | false | 0.070770 | 0.282013 | 0.531049 | 0.492003 |
| DS-002 | 3842 | pass | fail | full_signal | false | 0.050366 | 0.249475 | 0.499475 | 0.412303 |
| DS-002 | 3866 | fail | pass | high_signal | true | 0.036330 | 0.115078 | 0.339232 | 0.295967 |
| DS-002 | 3868 | pass | fail | full_signal | false | 0.060961 | 0.251419 | 0.501417 | 0.524265 |
| DS-002 | 3903 | pass | fail | full_signal | false | 0.052519 | 0.220003 | 0.469045 | 0.408134 |
| DS-002 | 3921 | fail | pass | high_signal | true | 0.038614 | 0.175009 | 0.418340 | 0.496241 |
| DS-002 | 3932 | pass | fail | full_signal | false | 0.088628 | 0.376663 | 0.613729 | 0.543404 |
| DS-002 | 3942 | pass | fail | full_signal | false | 0.063709 | 0.273596 | 0.523064 | 0.433083 |
| DS-002 | 3964 | fail | pass | high_signal | true | 0.031796 | 0.150426 | 0.387848 | 0.645181 |
| DS-002 | 3972 | pass | fail | full_signal | false | 0.053744 | 0.245499 | 0.495479 | 0.369856 |
| DS-002 | 3977 | pass | fail | full_signal | false | 0.052465 | 0.193768 | 0.440191 | 0.411620 |
| DS-002 | 3980 | fail | pass | high_signal | true | 0.049748 | 0.225358 | 0.474719 | 0.439781 |
| DS-002 | 3990 | pass | fail | full_signal | false | 0.057547 | 0.237779 | 0.487626 | 0.498770 |
| DS-002 | 3991 | fail | pass | high_signal | true | 0.033636 | 0.162718 | 0.403383 | 0.351128 |
| DS-002 | 3992 | pass | fail | full_signal | false | 0.060311 | 0.169395 | 0.411577 | 0.431032 |
| DS-002 | 3998 | fail | pass | high_signal | true | 0.038907 | 0.106292 | 0.326024 | 0.378332 |
| DS-002 | 4024 | fail | pass | high_signal | true | 0.022947 | 0.070311 | 0.265163 | 0.348872 |
| DS-002 | 4036 | fail | pass | high_signal | true | 0.017848 | 0.075544 | 0.274854 | 0.427177 |
| DS-002 | 4041 | pass | fail | full_signal | false | 0.080078 | 0.349219 | 0.590947 | 0.573342 |
| DS-002 | 4045 | fail | pass | high_signal | true | 0.047432 | 0.180700 | 0.425088 | 0.602324 |
| DS-002 | 4050 | fail | pass | high_signal | true | 0.025956 | 0.063536 | 0.252063 | 0.265755 |
| DS-002 | 4064 | pass | fail | full_signal | false | 0.060846 | 0.298393 | 0.546254 | 0.554545 |
| DS-002 | 4092 | fail | pass | high_signal | true | 0.024262 | 0.068717 | 0.262139 | 0.341969 |
| DS-003 | 3707 | pass | fail | full_signal | false | 0.067330 | 0.154720 | 0.393345 | 0.305471 |
| DS-003 | 3730 | fail | pass | high_signal | true | 0.021105 | 0.078691 | 0.280518 | 0.433022 |
| DS-003 | 3754 | fail | pass | high_signal | true | 0.023912 | 0.124931 | 0.353455 | 0.382110 |
| DS-003 | 3788 | fail | pass | high_signal | true | 0.020961 | 0.100872 | 0.317604 | 0.422601 |
| DS-003 | 3811 | fail | pass | high_signal | true | 0.037268 | 0.106412 | 0.326209 | 0.344442 |
| DS-003 | 3832 | pass | fail | full_signal | false | 0.071269 | 0.216039 | 0.464800 | 0.506513 |
| DS-003 | 3866 | pass | fail | full_signal | false | 0.053006 | 0.144159 | 0.379682 | 0.403713 |
| DS-003 | 3870 | fail | pass | high_signal | true | 0.039507 | 0.111577 | 0.334031 | 0.431285 |
| DS-003 | 3917 | pass | fail | full_signal | false | 0.058117 | 0.203935 | 0.451591 | 0.316327 |
| DS-003 | 3921 | fail | pass | high_signal | true | 0.030990 | 0.077926 | 0.279153 | 0.345636 |
| DS-003 | 3932 | pass | fail | full_signal | false | 0.058917 | 0.175695 | 0.419160 | 0.409249 |
| DS-003 | 3942 | pass | fail | full_signal | false | 0.063640 | 0.221521 | 0.470661 | 0.428897 |
| DS-003 | 3948 | pass | fail | full_signal | false | 0.073222 | 0.224202 | 0.473500 | 0.437147 |
| DS-003 | 3961 | pass | fail | full_signal | false | 0.051876 | 0.187687 | 0.433229 | 0.290382 |
| DS-003 | 3964 | fail | pass | high_signal | true | 0.011659 | 0.066243 | 0.257378 | 0.606383 |
| DS-003 | 3968 | pass | fail | full_signal | false | 0.054761 | 0.148784 | 0.385725 | 0.387321 |
| DS-003 | 3973 | fail | pass | high_signal | true | 0.021626 | 0.065498 | 0.255926 | 0.500977 |
| DS-003 | 3981 | pass | fail | full_signal | false | 0.051480 | 0.138290 | 0.371873 | 0.326856 |
| DS-003 | 3988 | pass | fail | full_signal | false | 0.077580 | 0.304042 | 0.551400 | 0.468519 |
| DS-003 | 3996 | fail | pass | high_signal | true | 0.039500 | 0.158522 | 0.398149 | 0.565892 |
| DS-003 | 4011 | fail | pass | high_signal | true | 0.010002 | 0.057538 | 0.239871 | 0.331416 |
| DS-003 | 4037 | pass | fail | full_signal | false | 0.056194 | 0.198334 | 0.445347 | 0.446591 |
| DS-003 | 4058 | fail | pass | high_signal | true | 0.048561 | 0.169114 | 0.411234 | 0.633521 |
| DS-003 | 4071 | pass | fail | full_signal | false | 0.078154 | 0.220255 | 0.469313 | 0.483717 |
| DS-003 | 4090 | pass | fail | full_signal | false | 0.054748 | 0.099064 | 0.314744 | 0.309053 |
| DS-006 | 3606 | fail | pass | high_signal | true | 0.025491 | 0.088445 | 0.297397 | 0.419734 |
| DS-006 | 3617 | fail | pass | high_signal | true | 0.049126 | 0.224637 | 0.473959 | 0.459524 |
| DS-006 | 3626 | fail | pass | high_signal | true | 0.020929 | 0.153730 | 0.392084 | 0.331136 |
| DS-006 | 3636 | pass | fail | full_signal | false | 0.053767 | 0.354318 | 0.595246 | 0.610485 |
| DS-006 | 3650 | fail | pass | high_signal | true | 0.036578 | 0.135583 | 0.368216 | 0.367262 |
| DS-006 | 3654 | pass | fail | full_signal | false | 0.052971 | 0.441242 | 0.664260 | 0.694643 |
| DS-006 | 3661 | fail | pass | high_signal | true | 0.044122 | 0.291386 | 0.539802 | 0.492308 |
| DS-006 | 3673 | fail | pass | high_signal | true | 0.026465 | 0.097343 | 0.311998 | 0.707372 |
| DS-006 | 3683 | fail | pass | high_signal | true | 0.003845 | 0.074311 | 0.272600 | 0.357875 |
| DS-006 | 3686 | fail | pass | high_signal | true | 0.037909 | 0.319668 | 0.565392 | 0.522115 |
| DS-006 | 3690 | fail | pass | high_signal | true | 0.022420 | 0.253813 | 0.503798 | 0.484570 |
| DS-006 | 3696 | fail | pass | high_signal | true | 0.046262 | 0.296795 | 0.544789 | 0.542857 |
| DS-006 | 3700 | fail | pass | high_signal | true | 0.024176 | 0.132170 | 0.363552 | 0.263462 |
| DS-006 | 3705 | fail | pass | high_signal | true | 0.041926 | 0.180245 | 0.424553 | 0.461630 |
| DS-006 | 3712 | fail | pass | high_signal | true | 0.030655 | 0.118862 | 0.344764 | 0.418636 |
| DS-006 | 3723 | fail | pass | high_signal | true | 0.044999 | 0.147500 | 0.384058 | 0.551236 |
| DS-006 | 3732 | pass | fail | full_signal | false | 0.065663 | 0.264322 | 0.514122 | 0.506319 |
| DS-006 | 3739 | fail | pass | high_signal | true | 0.040003 | 0.148196 | 0.384962 | 0.348260 |
| DS-006 | 3744 | fail | pass | high_signal | true | 0.048418 | 0.221333 | 0.470460 | 0.745650 |
| DS-006 | 3746 | fail | pass | high_signal | true | 0.025645 | 0.085195 | 0.291882 | 0.440385 |
| DS-006 | 3750 | fail | pass | high_signal | true | 0.045624 | 0.210431 | 0.458727 | 0.362637 |
| DS-006 | 3751 | fail | pass | high_signal | true | 0.036259 | 0.142175 | 0.377061 | 0.547253 |
| DS-006 | 3754 | fail | pass | high_signal | true | 0.018966 | 0.258169 | 0.508103 | 0.565339 |
| DS-006 | 3758 | fail | pass | high_signal | true | 0.043078 | 0.246888 | 0.496879 | 0.478159 |
| DS-006 | 3761 | fail | pass | high_signal | true | 0.037844 | 0.112980 | 0.336125 | 0.347024 |
| DS-006 | 3762 | fail | pass | high_signal | true | 0.009774 | 0.062158 | 0.249314 | 0.346841 |
| DS-006 | 3771 | fail | pass | high_signal | true | 0.047385 | 0.200612 | 0.447897 | 0.399405 |
| DS-006 | 3772 | fail | pass | high_signal | true | 0.045181 | 0.141097 | 0.375628 | 0.371932 |
| DS-006 | 3777 | pass | fail | full_signal | false | 0.052454 | 0.214108 | 0.462718 | 0.348764 |
| DS-006 | 3778 | fail | pass | high_signal | true | 0.029878 | 0.180334 | 0.424658 | 0.346062 |
| DS-006 | 3780 | fail | pass | high_signal | true | 0.046072 | 0.333202 | 0.577236 | 0.480815 |
| DS-006 | 3792 | fail | pass | high_signal | true | 0.049651 | 0.225217 | 0.474570 | 0.485623 |
| DS-006 | 3795 | fail | pass | high_signal | true | 0.019532 | 0.078020 | 0.279321 | 0.579670 |
| DS-006 | 3797 | fail | pass | high_signal | true | 0.031014 | 0.261042 | 0.510923 | 0.494551 |
| DS-006 | 3799 | fail | pass | high_signal | true | 0.015173 | 0.088920 | 0.298195 | 0.618956 |
| DS-006 | 3802 | fail | pass | high_signal | true | 0.031953 | 0.119102 | 0.345111 | 0.504625 |
| DS-006 | 3803 | pass | fail | full_signal | false | 0.074776 | 0.308994 | 0.555872 | 0.533745 |
| DS-006 | 3809 | fail | pass | high_signal | true | 0.046054 | 0.237523 | 0.487364 | 0.446703 |
| DS-006 | 3812 | fail | pass | high_signal | true | 0.040691 | 0.206499 | 0.454422 | 0.535394 |
| DS-006 | 3816 | fail | pass | high_signal | true | 0.018465 | 0.055730 | 0.236072 | 0.561767 |
| DS-006 | 3832 | fail | pass | high_signal | true | 0.032721 | 0.209767 | 0.458003 | 0.450321 |
| DS-006 | 3836 | fail | pass | high_signal | true | 0.046482 | 0.273561 | 0.523031 | 0.552152 |
| DS-006 | 3840 | fail | pass | high_signal | true | 0.049430 | 0.350116 | 0.591706 | 0.604625 |
| DS-006 | 3842 | fail | pass | high_signal | true | 0.020387 | 0.243562 | 0.493520 | 0.542033 |
| DS-006 | 3846 | pass | fail | full_signal | false | 0.074062 | 0.277172 | 0.526471 | 0.691987 |
| DS-006 | 3847 | fail | pass | high_signal | true | 0.037931 | 0.263728 | 0.513544 | 0.587912 |
| DS-006 | 3861 | fail | pass | high_signal | true | 0.043901 | 0.250335 | 0.500335 | 0.444872 |
| DS-006 | 3872 | fail | pass | high_signal | true | 0.045672 | 0.140284 | 0.374544 | 0.531273 |
| DS-006 | 3877 | fail | pass | high_signal | true | 0.043554 | 0.318769 | 0.564596 | 0.566026 |
| DS-006 | 3878 | fail | pass | high_signal | true | 0.027326 | 0.195369 | 0.442005 | 0.432921 |
| DS-006 | 3903 | fail | pass | high_signal | true | 0.047513 | 0.204547 | 0.452269 | 0.419780 |
| DS-006 | 3907 | fail | pass | high_signal | true | 0.027624 | 0.083863 | 0.289591 | 0.684020 |
| DS-006 | 3917 | fail | pass | high_signal | true | 0.034387 | 0.156848 | 0.396040 | 0.474130 |
| DS-006 | 3921 | fail | pass | high_signal | true | 0.034964 | 0.330491 | 0.574883 | 0.507784 |
| DS-006 | 3926 | fail | pass | high_signal | true | 0.046710 | 0.225204 | 0.474557 | 0.365842 |
| DS-006 | 3931 | fail | pass | high_signal | true | 0.030733 | 0.199727 | 0.446908 | 0.438507 |
| DS-006 | 3940 | fail | pass | high_signal | true | 0.047051 | 0.315517 | 0.561709 | 0.545101 |
| DS-006 | 3942 | pass | fail | full_signal | false | 0.052511 | 0.267491 | 0.517195 | 0.481136 |
| DS-006 | 3947 | fail | pass | high_signal | true | 0.041768 | 0.206610 | 0.454544 | 0.450687 |
| DS-006 | 3956 | pass | fail | full_signal | false | 0.072465 | 0.315987 | 0.562127 | 0.570055 |
| DS-006 | 3966 | fail | pass | high_signal | true | 0.035607 | 0.201401 | 0.448777 | 0.473523 |
| DS-006 | 3972 | fail | pass | high_signal | true | 0.025944 | 0.234845 | 0.484608 | 0.483522 |
| DS-006 | 3973 | fail | pass | high_signal | true | 0.049877 | 0.313164 | 0.559611 | 0.574267 |
| DS-006 | 3978 | fail | pass | high_signal | true | 0.013994 | 0.091149 | 0.301910 | 0.482555 |
| DS-006 | 3980 | fail | pass | high_signal | true | 0.034131 | 0.262054 | 0.511912 | 0.474954 |
| DS-006 | 3985 | pass | fail | full_signal | false | 0.054230 | 0.272557 | 0.522070 | 0.598947 |
| DS-006 | 3987 | fail | pass | high_signal | true | 0.049445 | 0.249914 | 0.499914 | 0.488049 |
| DS-006 | 3992 | pass | fail | full_signal | false | 0.083256 | 0.470344 | 0.685817 | 0.664789 |
| DS-006 | 3993 | fail | pass | high_signal | true | 0.026199 | 0.210429 | 0.458725 | 0.508013 |
| DS-006 | 3994 | fail | pass | high_signal | true | 0.027211 | 0.063762 | 0.252511 | 0.396886 |
| DS-006 | 4001 | fail | pass | high_signal | true | 0.024924 | 0.121902 | 0.349144 | 0.435897 |
| DS-006 | 4009 | fail | pass | high_signal | true | 0.041257 | 0.210546 | 0.458852 | 0.371841 |
| DS-006 | 4014 | fail | pass | high_signal | true | 0.035981 | 0.195505 | 0.442159 | 0.443315 |
| DS-006 | 4016 | fail | pass | high_signal | true | 0.018267 | 0.084773 | 0.291159 | 0.428325 |
| DS-006 | 4019 | pass | fail | full_signal | false | 0.062284 | 0.308208 | 0.555165 | 0.487042 |
| DS-006 | 4025 | fail | pass | high_signal | true | 0.019282 | 0.125180 | 0.353808 | 0.353938 |
| DS-006 | 4027 | fail | pass | high_signal | true | 0.044359 | 0.197998 | 0.444970 | 0.379716 |
| DS-006 | 4031 | fail | pass | high_signal | true | 0.049932 | 0.144891 | 0.380645 | 0.264377 |
| DS-006 | 4044 | fail | pass | high_signal | true | 0.024024 | 0.271749 | 0.521296 | 0.487134 |
| DS-006 | 4050 | pass | fail | full_signal | false | 0.069324 | 0.206700 | 0.454643 | 0.440842 |
| DS-006 | 4052 | fail | pass | high_signal | true | 0.049149 | 0.113341 | 0.336661 | 0.508150 |
| DS-006 | 4057 | pass | fail | full_signal | false | 0.060840 | 0.232355 | 0.482032 | 0.549679 |
| DS-006 | 4064 | pass | fail | full_signal | false | 0.069802 | 0.401626 | 0.633740 | 0.604441 |
| DS-006 | 4066 | pass | fail | full_signal | false | 0.055589 | 0.309440 | 0.556273 | 0.565110 |
| DS-006 | 4067 | fail | pass | high_signal | true | 0.041244 | 0.330372 | 0.574780 | 0.595330 |
| DS-006 | 4070 | fail | pass | high_signal | true | 0.039016 | 0.091132 | 0.301880 | 0.411264 |
| DS-006 | 4077 | fail | pass | high_signal | true | 0.045068 | 0.221363 | 0.470492 | 0.448581 |
| DS-006 | 4081 | pass | fail | full_signal | false | 0.070630 | 0.434165 | 0.658912 | 0.642903 |
| DS-006 | 4082 | fail | pass | high_signal | true | 0.034470 | 0.192682 | 0.438955 | 0.321886 |
| DS-006 | 4083 | fail | pass | high_signal | true | 0.047627 | 0.199102 | 0.446208 | 0.413420 |
| DS-006 | 4097 | fail | pass | high_signal | true | 0.015025 | 0.052217 | 0.228510 | 0.558837 |
| DS-006 | 4099 | pass | fail | full_signal | false | 0.072105 | 0.452099 | 0.672383 | 0.663736 |

