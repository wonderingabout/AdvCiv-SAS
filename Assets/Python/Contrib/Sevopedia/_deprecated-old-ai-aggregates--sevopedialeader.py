# <!-- custom:
# --- AI Attributes (Raw and Aggregated) Displayed's SevoPedia Leader's code ---
# Created as part of AdvCiv-SAS improvements
# (c) 2025 wonderingabout & becomingthrough
# -->

# <!-- custom: old code, still at module level, functioning mostly great but unsued now (among inaccuracies 86 may be max in some attributes pacifist for example for gandhi despite it beign highest score and not 100, since these cna be inferred more easily as we have more attributes to display / that we display better go with this and unburden us/ourselves from it too, may be more accurate this way too as more a attrbutes display a wider range of ai behaviours, which was the original goal or / if not one of the main goals of the sevopedia ai personality panel was to represent ai leaders's behaviorus/trends/tendencies etc anyways in ana ccurate and detaied, informative manner, which seems more than fine now with this much mroe ai attrbutes isntead, some of which are ven (pre-)aggregated like contact attributes, emory attirbutes, or/and others etc.-->


# --- Cache aggregate scoring (with precomputed scales) ---
def cache_ai_aggregate_scores():
	"""
	Caches the computed AI aggregate scores (both median-based and average-based) for each leader.

	Calculates high-level aggregate behavioral scores (like "Warmonger", "Builder") by
	combining multiple normalized AI attributes with specific weights and inversion rules.

	- Each aggregate computes:
	  - Weighted average score (for raw value analysis).
	  - Weighted median score (for final display with symbolic scale).

	Globals Modified:
	- AI_AGGREGATE_SCORES (dict): Maps leader name -> { aggregate_label: (median_score, scale_string) }.
	- AI_AGGREGATE_RAW_SCORES (dict): Maps leader name -> { aggregate_label: average_score }.

	Assumptions:
	- Raw XML leader data is available in PARSED_XML_LEADERS_VALUES.
	- Normalization is performed using AI_VALUE_RANGES.
	- Aggregate field definitions are found in COMPUTED_AND_DISPLAYED_AI_AGGREGATES.
	- Inversion per attribute is controlled by ATTRIBUTE_INVERT_FLAGS.

	Behavior:
	- If an aggregate field is missing min/max or leader data, it is skipped.
	- Aggregates missing weight data or producing no values default to 0.
	- Final median-based scores are scaled visually with "#".

	Warnings:
	- Weighted median and weighted average are independently calculated.
	- Aggregate scores are clamped to a maximum of 100 to avoid overflow.
	"""
	global AI_AGGREGATE_SCORES, AI_AGGREGATE_RAW_SCORES
	AI_AGGREGATE_SCORES.clear()
	AI_AGGREGATE_RAW_SCORES.clear()

	symbol = AGGREGATED_SCALE_SYMBOL

	for leader in sorted(PARSED_XML_LEADERS_VALUES.keys()):
		if leader in EXCLUDED_LEADERS:
			continue

		agg_medians = {}
		agg_averages = {}

		for label, fields in COMPUTED_AND_DISPLAYED_AI_AGGREGATES:
			weighted_vals = []
			norm_vals_and_weights = []

			for attr, invert, weight in fields:
				# <!-- custom: expected check not a placeholder, some attributes are not numerical, (so if i am not mistaken) skip these from futher computation comparison -->
				if not AI_VALUE_RANGES.has_key(attr):
					continue

				raw_attrs = PARSED_XML_LEADERS_VALUES[leader]
				if attr not in raw_attrs:
					raise KeyError("Missing attribute %s for leader %s" % (attr, leader))
				raw_val = raw_attrs[attr]

				# Correct: use raw value from parsed XML
				raw_val = PARSED_XML_LEADERS_VALUES[leader][attr]

				min_val, max_val = AI_VALUE_RANGES[attr]
				if (raw_val < min_val) or (raw_val > max_val):
					raise ValueError("[FATAL] At AI_ATTRIBUTE_DATA's stage and before normalization, in attr=%s and in leader=%s, raw_val=%d cannot be strictly out of bounds of min_val=%d and max_val=%d")
				norm_val = normalize_to_100(raw_val, min_val, max_val, invert, attr)

				weighted_vals.append(norm_val * weight)
				norm_vals_and_weights.append((norm_val, weight))

			if weighted_vals:
				total_weight = sum([w for _, w in norm_vals_and_weights])
				if total_weight > 0:
					average_score = int(round(sum(weighted_vals) / total_weight))
				else:
					average_score = 0

				sorted_pairs = sorted(norm_vals_and_weights)
				cum_weight = 0.0
				median_score = 0
				for norm_val, weight in sorted_pairs:
					cum_weight += weight
					if cum_weight >= total_weight / 2.0:
						median_score = int(round(norm_val))
						break
			else:
				raise ValueError("Aggregate '%s' has no weighted values for leader %s" % (label, leader))

			# <!-- custom: very unlikely for aggregates that one aggregate would have the same value accross/among all leaders but (is) just to cover this edge case, it is not impossible depending on how they (aggregates) are defined anyways etc anyways
			# note: this does not take average scoring into account, would need to implement a proper min-max check into it for this, even though unlikely, may be ideally best to cover this edge case too, anyways etc anyways
			# but to collect and display this info if (an) aggregates(aggregate) were to be equal among/accross all leaders, either the normalize funciton would need to display or return it maybe rather but is quite hacky and unclean, or some storing min max currently logic would need to be impelmented, then rewriting symbols only after all computation is done (and relooping over eladers again, for example (there may be better or/and other ideas to impelent this, but as this si extremely unliekly avoiding this hassle, plus would need to do it for average scores too if one day we'd want to display them too (unliekly too but anyways who knows etc anyways, hopefully helpful etc anyways, anyways)))
			# -->

			if (symbol != AGGREGATED_SCALE_SYMBOL) and (symbol != EQUAL_SCALE_SYMBOL):
				raise ValueError("Unexpected symbol %s in aggregate %s: attribute %s and in leader %s.)" %(symbol, label, attr, leader))

			# Precompute scale for median score
			scale = get_symbol_scale(median_score, symbol)

			agg_medians[label] = (None, median_score, scale)
			agg_averages[label] = min(average_score, 100)

		AI_AGGREGATE_SCORES[leader] = agg_medians
		AI_AGGREGATE_RAW_SCORES[leader] = agg_averages

		# --- Compact Debug Output for AI_AGGREGATE_SCORES ---
		line = "[DEBUG] Cached AI aggregate scores for leader %s: " % leader
		pairs = []
		for label in sorted(agg_medians.keys()):
			none_val, med_score, scale = agg_medians[label]
			avg_score = AI_AGGREGATE_RAW_SCORES[leader][label]
			pairs.append("%s=(%s, median=%d, average=%d,\"%s\")" % (label, none_val, med_score, avg_score, scale))
		line += "{ " + ", ".join(pairs) + " }"
		CvUtil.pyPrint(line)

	CvUtil.pyPrint("[DEBUG] Cached aggregate scores for %d leaders" % len(AI_AGGREGATE_SCORES))

	# <!-- custom: (some) extra sanity checks -->
	for leader_key in EXCLUDED_LEADERS:
		if (leader_key in AI_AGGREGATE_RAW_SCORES.keys()):
			raise KeyError("[FATAL] At AI_AGGREGATE_RAW_SCORES post-processing('s) testing, leader_key=%s was not properly eliminated/excluded and is still part of the data" % leader_key)
		
cache_ai_aggregate_scores()



# However, in future we may want to render AI_AGGREGATE_RAW_SCORES (average) alongside or as a tooltip, toggle, or legend.
# For now, averages are computed and stored, but not shown.



# <!-custom: then at ui level in place ai personality panel code was -->



	# <!-- custom: based on placeHistory then tweaked or/and modified or/and not
	# also data fetching logic mostly if not entirely provided by ChatGPT, or/and with
	# some additions or modifications or removals or other i did or did not, anyways

	#<!-- custom: link not working to concept page of ai personality, disabling it for now, if not always or not etc anyways, -->

					# <!-- custom: for ai aggregates, hide header to gain some room to display more
					# aggregates, plus is redundant with the panel header TXT_KEY_AI_PERSONALITY_RIGHT_PANEL.
					# We (me and chatgpt my friend etc but anyways) could have made several AI
					# aggregates categories like for the raw AI attributes, but we would have lost
					# several rows. While not initially intentional, this design/intent to have no
					# header for ai aggregates while still keeping the same type of "container"
					# (AI_HEADER_AGGREGATES) allows this code to be versatile and modular perhaps.
					# Could be slightly optiized by dynamically fetching categories last id and
					# automatically spacing instead of using line breaks, but works now and hopefully
					# straightforward enough and a bit easier to maintain perhaps.
					# May tweak it later or not, for now works and is functionnal enough, not a so
					# bad or terrible or hideous design maybe, like the "#" and  "+" functions maybe,
					# anyways.

					# <!-- custom: display ai aggregates -->

					# <!-- custom: display raw ai attributes -->



# --- Place AI Personality Panel (using precomputed scales) ---
def placeAIPersonalityPanel(self, iLeaderType):
	"""
	Renders the full AI Personality panel in the Sevopedia Leader page using
	precomputed and normalized AI data for the given leader.

	Displays all raw AI attributes and derived aggregates in a structured,
	three-column layout. The panel consists of three vertical sections
	(right, middle, left), each containing grouped categories of AI personality data.
	Every attribute is shown with its label, numeric value, and symbolic scale (e.g., "+++").

	Each data row is derived directly from:
	- `AI_ATTRIBUTE_DATA`: Raw XML attribute values normalized to 0–100 and converted to scale.
	- `AI_AGGREGATE_SCORES`: Median-based symbolic display scores for aggregates.

	Panel setup:
	- Right: Aggregates and Religion-related modifiers.
	- Middle: Core traits, Flavors, Victory weights, War strategies.
	- Left: Economic traits, refusal thresholds, diplomacy contact chances, modifiers.

	Design Principles:
	- **Strictly no placeholders**: All data accesses are direct and unconditional.
	Missing or misconfigured data will raise exceptions by design, ensuring
	bugs or omissions surface immediately.
	- Attributes that represent contact probabilities (e.g., iContactXxxProb) display
	contextual (delay/rand) info as part of the label (e.g., "Contact (3/50)").
	- Aggregates are grouped with spacing breaks (from `AI_AGGREGATES_CATEGORY_BREAKS`)
	and rendered using "#" scale symbols.

	Assumptions:
	- `AI_ATTRIBUTE_DATA` and `AI_AGGREGATE_SCORES` must be fully precomputed before rendering.
	- `DISPLAYED_AI_ATTRIBUTE_CATEGORIES` must include all expected category keys and mappings.
	- No leader data may be missing. All required fields must exist in the cache.

	Globals Used (read-only):
	- AI_ATTRIBUTE_DATA (dict): Maps leader -> { attr -> (raw_val, norm_val, scale) }
	- AI_AGGREGATE_SCORES (dict): Maps leader -> { label -> (None, median_score, scale) }
	- COMPUTED_AND_DISPLAYED_AI_AGGREGATES (list): Ordered aggregate definitions.
	- DISPLAYED_AI_ATTRIBUTE_CATEGORIES (dict): Category -> [(label, attr, core_name)]
	- AGGREGATED_CONTACT_PROBABILITY_ATTRIBUTES (set): Attributes using delay/rand contextual labels.

	Exceptions:
	- Raises `KeyError` if any attribute, category, or leader data is missing.
	- Intended to fail fast if cache generation was incomplete or misconfigured.

	Typical Use:
	- Called automatically when opening the Sevopedia Leader page.
	- Should follow a successful call to all cache functions:
	`cache_ai_value_ranges()`, `cache_ai_attribute_data()`, `cache_ai_aggregate_scores()`.
	"""
	screen = self.top.getScreen()

	def getXPanelCoordinate(tableId):
		return self.X_AI_PERSONALITY - tableId * self.W_AI_PERSONALITY - tableId * self.MEDIUM_MARGIN

	# === Layout constants ===
	xPanelRight = getXPanelCoordinate(self.N_AI_TABLE_NUM - 3)
	xPanelMiddle = getXPanelCoordinate(self.N_AI_TABLE_NUM - 2)
	xPanelLeft = getXPanelCoordinate(self.N_AI_TABLE_NUM - 1)
	yPanel = self.Y_AI_PERSONALITY + self.H_AI_UPPER_PADDING

	def setupPanel(screen, txtKey, xPanel):
		panelName = self.top.getNextWidgetName()
		screen.addPanel(
			panelName,
			localText.getText(txtKey, ()),
			"",
			True,
			True,
			xPanel,
			self.Y_AI_PERSONALITY,
			self.W_AI_PERSONALITY,
			self.H_AI_PERSONALITY,
			PanelStyles.PANEL_STYLE_BLUE50
		)

	# === PANEL SETUP ===
	setupPanel(screen, "TXT_KEY_AI_PERSONALITY_RIGHT_PANEL", xPanelRight)
	setupPanel(screen, "TXT_KEY_AI_PERSONALITY_MIDDLE_PANEL", xPanelMiddle)
	setupPanel(screen, "TXT_KEY_AI_PERSONALITY_LEFT_PANEL", xPanelLeft)

	# === Category Lists ===
	right_categories = [
		AI_HEADER_ECONOMIC_PREFERENCES,
		AI_HEADER_REFUSAL_THRESHOLDS,
		AI_HEADER_DIPLOMACY_AGGREGATED_CONTACT_PROBABILITIES,
		AI_HEADER_MODIFIERS,
		AI_HEADER_RELIGIONS_ATTITUDE_CHANGES_OR_AND_LIMITS_OR_AND_DIVISORS,
	]
	middle_categories = [
		AI_HEADER_POSITIVE_MEMORY_AFFECTIONS,
		# <!-- custom: not used in AdvCiv-SAS and also not in AdvCiv-AdvCiv-SAS's data, no bitterly ungrateful AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_POSITIVE_MEMORY_RESENTMENTS, -->
		AI_HEADER_NEGATIVE_MEMORY_RESENTMENTS,
		# <!-- custom: not used in AdvCiv-AdvCiv-SAS's data, no masochistic :o (would be fun even nice maybe but anyways, not that i dislike nor do i especially want.. but anyways etc anyways...) AI in AdvCiv/AdvCiv-SAS at least not now hehe (i don't think i'll change it (for AdvCiv-SAS i or the AdvCiv-SAS authors (including becomingthrough/chatgpt at least hehe but anyways) hehe will change it anyways etc), but if i want the tools are there, anyways etc anyways) AI_HEADER_NEGATIVE_MEMORY_AFFECTIONS, -->
		AI_HEADER_NO_WAR_AT,
	]
	left_categories = [
		AI_HEADER_CORE_PERSONALITY,
		AI_HEADER_VICTORY_WEIGHTS,
		AI_HEADER_FLAVORS,
		AI_HEADER_WAR_STRATEGY,
	]

	def fillTableRow(screen, label, value, scale, xLabel, xValue, xScale, y):
		labelText = u"<font=2>%s</font>" % label
		valueText = u"<font=2b>%d</font>" % value
		scaleText = u"<font=2>%s</font>" % scale

		screen.setText(self.top.getNextWidgetName(), "", labelText,
			CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT,
			WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", valueText,
			CvUtil.FONT_LEFT_JUSTIFY, xValue, y, 0, FontTypes.SMALL_FONT,
			WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "", scaleText,
			CvUtil.FONT_LEFT_JUSTIFY, xScale, y, 0, FontTypes.SMALL_FONT,
			WidgetTypes.WIDGET_GENERAL, -1, -1)

	# === Render Function ===
	def render_categories(screen, categories, xPanel, yPanel):
		xLabel = xPanel + self.W_AI_LEFT_SIDE_PADDING
		xValue = xLabel + self.W_AI_LABEL
		xScale = xValue + self.W_AI_VALUE
		y = yPanel

		first = True
		for category in categories:
			if not first:
				y += self.H_AI_CATEGORY_SPACING
			else:
				first = False

			# --- Category Header ---
			if category != AI_HEADER_AGGREGATES:
				screen.setText(self.top.getNextWidgetName(), "", u"<font=3b>%s</font>" % category,
					CvUtil.FONT_LEFT_JUSTIFY, xLabel, y, 0, FontTypes.SMALL_FONT,
					WidgetTypes.WIDGET_GENERAL, -1, -1)
				y += self.H_AI_LINE_HEIGHT

			# --- Display Aggregates ---
			if category == AI_HEADER_AGGREGATES:
				for idx, (label, _) in enumerate(COMPUTED_AND_DISPLAYED_AI_AGGREGATES):
					if idx in AI_AGGREGATES_CATEGORY_BREAKS:
						y += self.H_AI_CATEGORY_SPACING
					_, median_score, scale = AI_AGGREGATE_SCORES[iLeaderType][label]
					fillTableRow(screen, label, median_score, scale, xLabel, xValue, xScale, y)
					y += self.H_AI_LINE_HEIGHT
				continue

			# --- Display Raw and Aggregated AI Attributes ---
			for label, attr, core_name in DISPLAYED_AI_ATTRIBUTE_CATEGORIES[category]:
				# --- Contact Probabilities ---
				if attr in AGGREGATED_CONTACT_PROBABILITY_ATTRIBUTES:
					delay_field = "iContact%sDelayRaw" % core_name
					rand_field = "iContact%sRandRaw" % core_name
					delay_data = AI_ATTRIBUTE_DATA[iLeaderType][delay_field]
					rand_data = AI_ATTRIBUTE_DATA[iLeaderType][rand_field]
					delay_value = delay_data[0]
					rand_value  = rand_data[0]

					raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderType][attr]
					label = u"%s (%d/%d)" % (label, delay_value, rand_value)
				
				# --- Positive Memory Affection/Resentment ---
				elif attr in AGGREGATED_POSITIVE_MEMORY_AFFECTION_AND_RESENTMENT_ATTRIBUTES:
					att_field = "iPositiveMemoryAttitude%sRaw" % core_name
					dec_field = "iPositiveMemoryDecay%sRaw" % core_name
					att_value = AI_ATTRIBUTE_DATA[iLeaderType][att_field][0]
					dec_value = AI_ATTRIBUTE_DATA[iLeaderType][dec_field][0]
					raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderType][attr]
					label = u"%s (+%d/%d)" % (label, att_value, dec_value)

				# --- Negative Memory Affection/Resentment ---
				elif attr in AGGREGATED_NEGATIVE_MEMORY_RESENTMENT_AND_AFFECTION_ATTRIBUTES:
					att_field = "iNegativeMemoryAttitude%sRaw" % core_name
					dec_field = "iNegativeMemoryDecay%sRaw" % core_name
					att_value = AI_ATTRIBUTE_DATA[iLeaderType][att_field][0]
					dec_value = AI_ATTRIBUTE_DATA[iLeaderType][dec_field][0]
					raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderType][attr]
					label = u"%s (%d/%d)" % (label, att_value, dec_value)

				else:
					raw_val, norm_val, scale = AI_ATTRIBUTE_DATA[iLeaderType][attr]

				fillTableRow(screen, label, norm_val, scale, xLabel, xValue, xScale, y)
				y += self.H_AI_LINE_HEIGHT

	# Render Panels
	render_categories(screen, right_categories, xPanelRight, yPanel)
	render_categories(screen, middle_categories, xPanelMiddle, yPanel)
	render_categories(screen, left_categories, xPanelLeft, yPanel)