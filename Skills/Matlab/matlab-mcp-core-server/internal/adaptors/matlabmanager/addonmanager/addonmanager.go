// Copyright 2026 The MathWorks, Inc.

package addonmanager

import (
	"context"

	"github.com/matlab/matlab-mcp-core-server/internal/adaptors/time/retry"
	"github.com/matlab/matlab-mcp-core-server/internal/entities"
	"github.com/matlab/matlab-mcp-core-server/internal/messages"
)

type InstallationSteps interface {
	UploadMLTBX(ctx context.Context, logger entities.Logger, client entities.MATLABSessionClient) (func(), messages.Error)
	VerifyMLTBXInstallationFile(ctx context.Context, logger entities.Logger, client entities.MATLABSessionClient) messages.Error
	InstallMLTBX(ctx context.Context, logger entities.Logger, client entities.MATLABSessionClient) messages.Error
}

type AddonManager struct {
	installationSteps InstallationSteps
}

func New(
	installationSteps InstallationSteps,
) *AddonManager {
	return &AddonManager{
		installationSteps: installationSteps,
	}
}

func (a *AddonManager) Install(ctx context.Context, logger entities.Logger, client entities.MATLABSessionClient) messages.Error {
	logger.Debug("Installing MATLAB Add-On")

	cleanup, err := a.installationSteps.UploadMLTBX(ctx, logger, client)
	if err != nil {
		return err
	}
	defer cleanup()

	err = a.installationSteps.VerifyMLTBXInstallationFile(ctx, logger, client)
	if err != nil {
		return err
	}

	// installToolbox sometimes throws strange errors, which go away on retry
	var lastErr messages.Error
	_, retryErr := retry.Retry(ctx, func() (struct{}, bool, error) {
		lastErr = a.installationSteps.InstallMLTBX(ctx, logger, client)
		if lastErr != nil {
			return struct{}{}, false, nil
		}

		return struct{}{}, true, nil
	}, retry.NewFixedCountRetryStrategy(2))

	if retryErr != nil {
		if lastErr != nil {
			return lastErr
		}
		logger.
			WithError(retryErr).
			Error("Failed to install MLTBX in MATLAB")
		return messages.New_AddonManagerErrors_InstallFailed_Error()
	}

	logger.Info("MATLAB Add-On installation complete")

	return nil
}
