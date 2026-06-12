from config import EXERCISES, DEFAULT_EXERCISE, ASYMMETRY_THRESHOLD

def analyze_posture(angles, exercise=DEFAULT_EXERCISE):
    print("CURRENT EXERCISE =", exercise)

    issues = []
    status = "Good"

    ex = EXERCISES.get(exercise, EXERCISES[DEFAULT_EXERCISE])

    knee_min     = ex["knee_min"]
    knee_max     = ex["knee_max"]
    spine_min    = ex["spine_min"]
    shoulder_min = ex["shoulder_min"]

    left_knee  = angles.get("left_knee")
    right_knee = angles.get("right_knee")
    spine      = angles.get("spine")
    shoulder   = angles.get("shoulder")

    
    # WARRIOR POSE LOGIC
    
    if exercise == "warrior":

        
        # Knee posture
        

        if left_knee is not None and right_knee is not None:

            bent_leg_ok = (
                80 <= left_knee <= 130 or
                80 <= right_knee <= 130
            )

            straight_leg_ok = (
                left_knee >= 150 or
                right_knee >= 150
            )

            if not bent_leg_ok:
                issues.append("Front knee posture incorrect")

            if not straight_leg_ok:
                issues.append("Back leg should remain straighter")

        
        # Torso posture
        

        # Warrior pose should keep torso mostly upright
        if spine is not None and spine < 165:
            issues.append("Upper body leaning too much")

        
        # Arm alignment
        

        if shoulder is not None and shoulder < 75:
            issues.append("Arms not properly aligned")

        # Detect uneven arms
        if angles.get("shoulder_asymmetry") is not None:
            if angles["shoulder_asymmetry"] > 10:
                issues.append("Arms are unevenly aligned")

    
    # DEFAULT LOGIC FOR OTHER EXERCISES
    

    else:

        # Left knee
        if left_knee is not None:
            if left_knee < knee_min:
                issues.append("Left knee bent too much")
            elif left_knee > knee_max:
                issues.append("Left knee not bent enough")

        # Right knee
        if right_knee is not None:
            if right_knee < knee_min:
                issues.append("Right knee bent too much")
            elif right_knee > knee_max:
                issues.append("Right knee not bent enough")

        # Spine
        if spine is not None:
            if spine < spine_min:
                issues.append("Spine not straight")

        # Shoulder
        if shoulder is not None:
            if shoulder < shoulder_min:
                issues.append("Shoulder position incorrect")

        # Asymmetry only for normal exercises
        if angles.get("knee_asymmetry") is not None:
            if angles["knee_asymmetry"] > ASYMMETRY_THRESHOLD:
                issues.append(
                    f"Knee asymmetry: {angles['knee_asymmetry']} deg difference"
                )

        if angles.get("shoulder_asymmetry") is not None:
            if angles["shoulder_asymmetry"] > ASYMMETRY_THRESHOLD:
                issues.append(
                    f"Shoulder asymmetry: {angles['shoulder_asymmetry']} deg difference"
                )

    

    if len(issues) > 0:
        status = "Needs correction"

    return {
        "status": status,
        "issues": issues,
        "exercise": exercise
    }