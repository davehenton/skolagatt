# Samræmd
/samraemd

	# Niðurstöður
	/niðurstöður
		# Hrágögn
		/rawdata							=> Setja inn hrágögn

		# Niðurstöður tiltekinna skóla
		/(School_id) 						=> Listi af niðurstöðum fyrir skóla
			/(year)/(group) 				=> Skoða tilteknar niðurstöður
				/excel						=> Sækja niðurstöður sem Excel
				/einkunnablod 				=> Einkunnablöð fyrir tilteknar niðurstöður
				/hrágögn 					=> Hrágögn fyrir tilteknar niðurstöður
					/einkunnablod 			=> Einkunnablöð fyrir hrágögn
		# Stærðfræði niðurstöður
		/stæ/								=> Allar Stæ niðurstöður fyrir stjórnendur
			/(School_id) 					=> Listi af stæ niðurstöðum fyrir skóla
			/niðurstöður/create				=> Skrá niðurstöður fyrir stæ
			/niðurstöður/(exam_code)/delete	=> Eyða stæ niðurstöðum
		# Íslenska
		/isl/								=> Allar ÍSL niðurstöður fyrir stjórnendur
			/(School_id) 					=> Listi af ÍSL niðurstöðum fyrir skóla
			/niðurstöður/create				=> Skrá niðurstöður fyrir ÍSL
			/niðurstöður/(exam_code)/delete	=> Eyða ÍSL niðurstöðum
	# Stjórnendasýn
	/umsjónarmaður/
		# Stærðfræði niðurstöður
		/stæ/niðurstöður/(year)/(group)/	=> Stæ niðurstöður fyrir tiltekið próf
		# Íslensku niðurstöður
		/isl/niðurstöður/(year)/(group)/	=> ÍSL niðurstöður fyrir tiltekið próf
		# Aðrar niðurstöður
		/niðurstöður
			/(exam_code)/(year)/(group)		=> Skoða nðurstöður tiltekins prófs
				/rawexcel					=> Hlaða niður sem Excel
				/einkunnablod				=> Prentanleg einkunnablöð


# Stuðningsúrræði
/stuðningur
	# API
	/api 									=> Vefþjónustu endapunktur fyrir stuðningsúrræði
	# Skóli
	/(school_id)							=> Stuðningsúrræði fyrir tiltekinn skóla
		/nemandi
			/(pk)							=> Yfirlit um stuðning fyrir tiltekinn nemanda
				/stuðningsúrræði 			=> Setja inn stuðningsúrræði
				/undanþágur 				=> Setja inn undanþágur

# Prófagrunnur
/profagrunnur
	# Próf
	/										=> Listi yfir öll próf
	/api 									=> API endapunktur fyrir öll próf
		/(survey_id)						=> API endapunktur fyrir tiltekið próf
	/create									=> Búa til nýtt próf
	/(survey_id)									=> Upplýsingar um tiltekið próf
		/update								=> Breyta prófi
		/delete								=> Eyða prófi
		# Öll eigindi undir prófi eru með sömu slóðir
		/resource, /template, /input, /group
			/create							=> Bæta eigindi við próf
			/(survey_text_id)				=> Skoða tiltekið eigindi við próf
				/update						=> Breyta eigindi
				/delete						=> Eyða eigindi
