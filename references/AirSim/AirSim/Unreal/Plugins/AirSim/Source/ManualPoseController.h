#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerInput.h"

#include "ManualPoseController.generated.h"

UCLASS()
class AIRSIM_API UManualPoseController : public UObject
{
    GENERATED_BODY()

public:
    void initializeForPlay();
    void setActor(AActor* actor);
    AActor* getActor() const;
    void updateActorPose(float dt);
    void getDeltaPose(FVector& delta_position, FRotator& delta_rotation) const;
    void resetDelta();
    void updateDeltaPosition(float dt);

private:
    void inputManualLeft(float val);
    void inputManualRight(float val);
    void inputManualForward(float val);
    void inputManualBackward(float val);
    void inputManualMoveUp(float val);
    void inputManualDown(float val);
    void inputManualLeftYaw(float val);
    void inputManualRightYaw(float val);
    void inputManualLeftRoll(float val);
    void inputManualRightRoll(float val);
    void inputManualUpPitch(float val);
    void inputManualDownPitch(float val);
    void inputManualSpeedIncrease(float val);
    void inputManualSpeedDecrease(float val);
    void inputManualMouseLook(float val);
    void inputManualMouseYaw(float val);
    void inputManualMousePitch(float val);

    void setupInputBindings();
    void removeInputBindings();
    void clearBindings();

private:
    FInputAxisBinding *left_binding_, *right_binding_, *up_binding_, *down_binding_;
    FInputAxisBinding *forward_binding_, *backward_binding_, *left_yaw_binding_, *right_yaw_binding_;
    FInputAxisBinding *up_pitch_binding_, *down_pitch_binding_, *left_roll_binding_, *right_roll_binding_;
    FInputAxisBinding *inc_speed_binding_, *dec_speed_binding_;
    FInputAxisBinding *mouse_look_binding_, *mouse_yaw_binding_, *mouse_pitch_binding_;

    FInputAxisKeyMapping left_mapping_, right_mapping_, up_mapping_, down_mapping_;
    FInputAxisKeyMapping forward_mapping_, backward_mapping_, left_yaw_mapping_, right_yaw_mapping_;
    FInputAxisKeyMapping up_pitch_mapping_, down_pitch_mapping_, left_roll_mapping_, right_roll_mapping_;
    FInputAxisKeyMapping inc_speed_mapping_, dec_speed_mapping_;
    FInputAxisKeyMapping mouse_look_mapping_, mouse_yaw_mapping_, mouse_pitch_mapping_;

    FVector delta_position_;
    FRotator delta_rotation_;

    AActor* actor_;

    float acceleration_ = 0, speed_scaler_ = 1000;
    float keyboard_rotation_scaler_ = 0.1f;
    float mouse_sensitivity_ = 0.15f;
    bool mouse_look_active_ = false;
    FVector input_positive_, inpute_negative_;
    FVector last_velocity_;
};
